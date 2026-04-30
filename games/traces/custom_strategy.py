"""Custom strategy extending ppbench BasicAgenticSolve.

Injects custom R6-R8 rules into prompts, adds screenshot context,
and validates custom rules in extract_result().
"""

import os
import yaml
from dataclasses import dataclass, field
from typing import Any, List

from pydantic_ai import Agent, RunContext, UsageLimits
from pydantic_ai.exceptions import ModelRetry

from ppbench.puzzle import Puzzle
from ppbench.benchmarks.strategy import AgentConfig, Strategy, StrategyResult
from ppbench.benchmarks.utils import StrategyLogger
from ppbench.benchmarks.strategies._helpers import (
    example_of_inputs,
    get_example_move_context,
    get_rules_for_puzzle,
)

from validators import (
    validate_move_ordering,
    validate_solution_constraints,
)

RULES_PATH = os.path.join(os.path.dirname(__file__), "custom_rules.yaml")

_rules_cache = None


def _load_rules() -> dict:
    global _rules_cache
    if _rules_cache is None:
        with open(RULES_PATH) as f:
            _rules_cache = yaml.safe_load(f)
    return _rules_cache


def get_custom_rules_text(pid: str) -> str:
    rules = _load_rules()
    entry = rules.get(pid)
    if not entry:
        return ""

    lines = []
    lines.append(f"=== CUSTOM RULES for {entry.get('name', pid)} ===")

    std = entry.get("standard_rules", {})
    for key in sorted(std.keys()):
        lines.append(f"  {key}: {std[key]}")

    custom = entry.get("custom_rules", {})
    if custom:
        lines.append("\n  ADDITIONAL CUSTOM RULES (you MUST follow these):")
        for key in sorted(custom.keys()):
            rule = custom[key]
            rtype = rule.get("type", "unknown")
            check = rule.get("check", "unknown")
            lines.append(f"  {key} [{rtype}, checked at {check}]: {rule['text']}")

    controls = entry.get("controls", [])
    if controls:
        lines.append("\n  CONTROLS:")
        for ctrl in controls:
            lines.append(f"    - {ctrl}")

    return "\n".join(lines)


@dataclass
class CustomAgenticContext:
    puzzle: Puzzle
    puzzle_data: dict
    log: StrategyLogger = field(default_factory=StrategyLogger)
    list_of_moves: list[str] = field(default_factory=list)
    gave_up: bool = False
    board_screenshots: list[bytes] = field(default_factory=list)


class CustomAgenticSolve(Strategy):
    requires_tools = True
    MAX_MOVES = 5000

    def __init__(self, puzzle_data: dict | None = None):
        self.puzzle_data = puzzle_data or {}

    def build_agent(self, puzzle: Any, model_obj: Any, model_name: str) -> AgentConfig:
        ticks = "```"
        pid = self.puzzle_data.get("pid", puzzle.pid)

        custom_rules_text = get_custom_rules_text(pid)
        standard_rules_text = get_rules_for_puzzle(puzzle)

        pre_post = ""
        try:
            pre_post = get_example_move_context(puzzle)
        except Exception:
            pass

        example_text = ""
        try:
            example_text = example_of_inputs(puzzle)
        except Exception:
            pass

        system_prompt = (
            "You are solving a logic puzzle. This is a benchmark — the puzzle is guaranteed solvable.\n"
            "You are graded on: (1) whether you solve it, (2) number of steps, (3) move count.\n"
            "You have tools to make moves, check the board, render it, and reset.\n"
            "IMPORTANT: This puzzle has CUSTOM RULES beyond standard rules. Read them carefully.\n"
            "If stuck, reset and try a different approach. Do not give up."
        )

        prompt_parts = [
            f"Puzzle Type: {pid}",
            f"\n--- STANDARD RULES ---\n{ticks}\n{standard_rules_text}\n{ticks}",
        ]

        if custom_rules_text:
            prompt_parts.append(f"\n--- CUSTOM RULES (MUST FOLLOW) ---\n{ticks}\n{custom_rules_text}\n{ticks}")

        if example_text:
            prompt_parts.append(f"\n--- EXAMPLES ---\n{ticks}\n{example_text}\n{ticks}")

        if pre_post:
            prompt_parts.append(f"\n--- MOVE EXAMPLE (before/after) ---\n{pre_post}")

        prompt_parts.append(
            "Note specifically how the coordinate systems work. "
            "Ensure your moves target exactly the cells you intend."
        )

        prompt_parts.append(
            f"\n==== PUZZLE TO SOLVE ====\n{puzzle.get_string_repr()}\n==== END PUZZLE ===="
        )
        prompt_parts.append("\nPlease solve it now.")

        prompt = "\n".join(prompt_parts)

        deps = CustomAgenticContext(
            puzzle=puzzle,
            puzzle_data=self.puzzle_data,
        )

        agent = Agent(
            model_obj,
            deps_type=CustomAgenticContext,
            output_retries=self.MAX_MOVES,
            system_prompt=system_prompt,
            retries=2,
        )

        @agent.output_validator
        async def keep_going_until_done(ctx: RunContext, out: str) -> str:
            ctx.deps.log.debug(
                f"Output: {out[:50]}...{out[-50:]} | "
                f"{len(ctx.deps.list_of_moves)} moves | "
                f"complete={ctx.deps.puzzle.isComplete()}"
            )
            if ctx.deps.gave_up:
                return out
            if len(ctx.deps.list_of_moves) < self.MAX_MOVES and not ctx.deps.puzzle.isComplete():
                raise ModelRetry(
                    "Not done yet! The puzzle isn't complete. "
                    "This puzzle is verified solvable. Keep going or reset and try again."
                )
            ctx.deps.log.info("Puzzle complete.")
            return out

        @agent.tool
        async def make_move(ctx: RunContext[CustomAgenticContext], movestring: str) -> str:
            ctx.deps.log.info(f"Move: {movestring}")
            try:
                ctx.deps.puzzle.send_move(movestring)
                ctx.deps.list_of_moves.append(movestring)
            except Exception as e:
                raise ModelRetry(str(e))
            return f"Move applied. Board state:\n{ctx.deps.puzzle.get_string_repr()}"

        @agent.tool
        async def make_multi_move(ctx: RunContext[CustomAgenticContext], movelist: List[str]) -> str:
            ctx.deps.log.info(f"Multi-move: {movelist}")
            try:
                for move in movelist:
                    ctx.deps.puzzle.send_move(move)
                    ctx.deps.list_of_moves.append(move)
            except Exception as e:
                raise ModelRetry(str(e))
            return f"Moves applied. Board state:\n{ctx.deps.puzzle.get_string_repr()}"

        @agent.tool
        async def check_board(ctx: RunContext[CustomAgenticContext]) -> str:
            return str(ctx.deps.puzzle.check())

        @agent.tool
        async def render_svg(ctx: RunContext[CustomAgenticContext]) -> str:
            return str(ctx.deps.puzzle.svg(True))

        @agent.tool
        async def get_rules(ctx: RunContext[CustomAgenticContext]) -> str:
            std = get_rules_for_puzzle(ctx.deps.puzzle)
            custom = get_custom_rules_text(ctx.deps.puzzle_data.get("pid", ctx.deps.puzzle.pid))
            return f"Standard:\n{std}\n\nCustom:\n{custom}"

        @agent.tool
        async def reset_puzzle(ctx: RunContext[CustomAgenticContext]) -> str:
            ctx.deps.puzzle = Puzzle.from_url(ctx.deps.puzzle.url)
            ctx.deps.list_of_moves = []
            return f"Puzzle reset. Board state:\n{ctx.deps.puzzle.get_string_repr()}"

        @agent.tool
        async def give_up(ctx: RunContext[CustomAgenticContext]) -> str:
            ctx.deps.gave_up = True
            return "You chose to give up. Tell me why."

        return AgentConfig(
            agent=agent,
            prompt=prompt,
            deps=deps,
            usage_limits=UsageLimits(
                request_limit=1e9,
                tool_calls_limit=1e9,
                input_tokens_limit=1e9,
                output_tokens_limit=1e9,
                total_tokens_limit=1e9,
            ),
        )

    def extract_logs(self, deps: Any) -> list:
        return deps.log.to_list()

    def extract_result(self, puzzle: Any, deps: Any, output: str) -> StrategyResult:
        moves = deps.list_of_moves
        puzzle_data = deps.puzzle_data
        pid = puzzle_data.get("pid", puzzle.pid)

        fresh = Puzzle.from_url(puzzle.url)
        for move in moves:
            fresh.send_move(move)

        base_solved = fresh.isComplete()

        r6_result = validate_move_ordering(pid, moves, puzzle_data)
        r78_result = validate_solution_constraints(pid, puzzle_data, {})

        detail = {
            "base_solved": base_solved,
            "r6_valid": r6_result["valid"],
            "r6_violations": r6_result.get("violations", []),
            "r78_valid": r78_result["valid"],
            "r78_violations": r78_result.get("violations", []),
            "total_moves": len(moves),
        }

        is_success = base_solved and r6_result["valid"] and r78_result["valid"]

        return StrategyResult(
            is_success=is_success,
            parsed_moves=moves,
            raw_output=output,
            detail_data=detail,
        )
