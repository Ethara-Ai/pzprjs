import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import yaml

TRACES_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TRACES_DIR)

from ppbench.puzzle import Puzzle
from ppbench.benchmarks.harness import run_strategy
from ppbench.benchmarks.model_list import get_model
from ppbench.benchmarks.utils import StorageManager, DetailedRunResult

from custom_strategy import CustomAgenticSolve


def load_config(config_path: str = None) -> dict:
    if config_path is None:
        config_path = os.path.join(TRACES_DIR, "config.yaml")
    with open(config_path) as f:
        return yaml.safe_load(f)


def load_dataset() -> list[dict]:
    dataset_path = os.path.join(TRACES_DIR, "dataset.jsonl")
    records = []
    with open(dataset_path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def filter_puzzles(records: list[dict], games: list[str] | None, difficulties: list[str] | None) -> list[dict]:
    if games:
        records = [r for r in records if r["pid"] in games]
    if difficulties:
        records = [r for r in records if any(r["puzzle_id"].endswith(f"_{d}") for d in difficulties)]
    return records


def make_output_dir(base_dir: str, model_name: str, pid: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_model = model_name.replace("/", "_").replace("@", "_")
    dirname = f"{timestamp}_{safe_model}_{pid}"
    out = Path(base_dir) / dirname
    out.mkdir(parents=True, exist_ok=True)
    return out


async def main(config_path: str = None):
    config = load_config(config_path)

    models = config.get("models", [])
    if not models:
        print("No models configured. Edit config.yaml.")
        return

    games_filter = config.get("games") or None
    diff_filter = config.get("difficulties") or None
    output_dir = config.get("output_dir", "runs")
    concurrency = config.get("concurrency", 5)

    records = load_dataset()
    records = filter_puzzles(records, games_filter, diff_filter)

    if not records:
        print("No puzzles matched filters.")
        return

    print(f"Puzzles: {len(records)}")
    print(f"Models: {models}")
    print(f"Total tasks: {len(records) * len(models)}")
    print(f"Concurrency: {concurrency}")
    print(f"Output: {output_dir}/")
    print()

    base_output = os.path.join(TRACES_DIR, output_dir)
    storage = StorageManager(base_dir=base_output)

    sem = asyncio.Semaphore(concurrency)
    all_results: list[DetailedRunResult] = []
    done_count = 0
    total_tasks = len(records) * len(models)
    start = time.time()

    async def run_one(record, model_name, model_obj):
        nonlocal done_count
        pid = record["pid"]
        puzzle_id = record.get("puzzle_id", pid)

        strategy = CustomAgenticSolve(puzzle_data=record)

        # Harness generates puzzle_id as f"{puzzle.pid}_{puzzle.id}" internally
        # We pre-create puzzle to get the real cache key
        url = record.get("puzzlink_url") or record.get("puzzle_url")
        puzzle = Puzzle.from_url(url)
        harness_puzzle_id = f"{puzzle.pid}_{puzzle.id}"

        cached = storage.lookup(strategy.strategy_id, model_name, harness_puzzle_id)
        if cached == "completed":
            done_count += 1
            elapsed = time.time() - start
            print(f"  [{done_count}/{total_tasks}] SKIP | {model_name} | {puzzle_id} | cached | [{elapsed:.0f}s]")
            return None

        async with sem:
            result = await run_strategy(
                strategy=strategy,
                puzzle=puzzle,
                model_obj=model_obj,
                model_name=model_name,
                storage=storage,
            )

        done_count += 1
        s = result.summary
        status = "PASS" if s.is_success else ("ERR" if s.error_type else "FAIL")
        elapsed = time.time() - start

        detail = result.detail_data or {}
        r6_ok = "✓" if detail.get("r6_valid", True) else "✗"
        r78_ok = "✓" if detail.get("r78_valid", True) else "✗"

        print(
            f"  [{done_count}/{total_tasks}] {status} | {model_name} | {puzzle_id} | "
            f"{s.duration_seconds:.1f}s | {s.total_requests} reqs | {len(s.parsed_moves)} moves | "
            f"R6:{r6_ok} R7-8:{r78_ok} | [{elapsed:.0f}s]"
        )

        run_dir = make_output_dir(base_output, model_name, puzzle_id)
        trace_path = run_dir / "trace.json"
        with open(trace_path, "w") as f:
            f.write(result.to_json())

        summary_path = run_dir / "summary.json"
        summary = {
            "puzzle_id": puzzle_id,
            "model": model_name,
            "is_success": s.is_success,
            "base_solved": detail.get("base_solved", False),
            "r6_valid": detail.get("r6_valid"),
            "r78_valid": detail.get("r78_valid"),
            "r6_violations": detail.get("r6_violations", []),
            "r78_violations": detail.get("r78_violations", []),
            "total_moves": len(s.parsed_moves),
            "duration_seconds": s.duration_seconds,
            "total_requests": s.total_requests,
            "error": s.error_type,
        }
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2, default=str)

        return result

    tasks = []
    for model_name in models:
        model_obj = get_model(model_name)
        for record in records:
            tasks.append(run_one(record, model_name, model_obj))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for r in results:
        if isinstance(r, DetailedRunResult):
            all_results.append(r)
        elif isinstance(r, Exception):
            print(f"  Task failed: {type(r).__name__}: {r}")

    elapsed = time.time() - start
    passed = sum(1 for r in all_results if r.summary.is_success)
    print(f"\nDone in {elapsed:.1f}s — {passed}/{len(all_results)} passed")


if __name__ == "__main__":
    config_file = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(main(config_file))
