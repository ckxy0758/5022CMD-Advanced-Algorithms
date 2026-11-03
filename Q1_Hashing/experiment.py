"""
Question 1, Task 4: compare search performance of the hash table (linear
probing) with a one-dimensional array (Python list + linear search).

Method
  1. For each dataset size n, create n products and insert the SAME products,
     in the SAME order, into both the hash table and the array.
  2. Search for the same set of keys in both structures:
       - First   : first inserted product  (best case for the array)
       - Middle  : product in the middle   (average case for the array)
       - Last    : last inserted product   (worst case for the array)
       - Missing : ID that does not exist  (array checks all n elements)
       - Random  : 1000 random existing IDs (typical use)
  3. Repeat each search many times and take the average per search, because
     one search takes only microseconds and a single timing is unreliable.
  4. Also record probes (hash table) and comparisons (array), which do not
     depend on the computer and link the timings to the theory.

Run:  python experiment.py            (full experiment, about 1-2 minutes)
      python experiment.py --quick    (smaller sizes, a few seconds)
Results are printed and saved to experiment_results.csv.
If matplotlib is installed, a chart is saved to experiment_chart.png.
"""

import csv
import platform
import random
import statistics
import sys
import time

from hash_table import HashTable
from array_search import linear_search
from product import Medicine

SIZES = [10, 100, 1_000, 10_000, 100_000]
QUICK_SIZES = [10, 100, 1_000, 5_000]
REPEATS = 5              # independent timing runs per case (median is reported)
RANDOM_KEYS = 1000       # number of random existing keys searched per run
SEED = 42                # fixed seed so the experiment is reproducible


# ---------------------------------------------------------------------- #
# Data generation
# ---------------------------------------------------------------------- #
def generate_products(n, seed=SEED):
    """Create n Medicine objects with unique IDs P000000, P000001, ..."""
    rng = random.Random(seed)
    products = []
    for i in range(n):
        products.append(Medicine(
            product_id=f"P{i:06d}",
            name=f"Medicine {i}",
            price=round(rng.uniform(1, 100), 2),
            stock_quantity=rng.randint(0, 500),
            manufacturer="Generic Pharma",
            expiry_date="2028-01-01",
            dosage="500mg tablet",
        ))
    return products


def build_structures(products):
    """Insert the same products, in the same order, into both structures."""
    table = HashTable()
    array = []
    for p in products:
        table.insert(p.product_id, p)
        array.append(p)
    return table, array


# ---------------------------------------------------------------------- #
# Timing
# ---------------------------------------------------------------------- #
def time_searches(search, keys, loops):
    """Average time (ns) of one search, over loops x len(keys) searches."""
    start = time.perf_counter_ns()
    for _ in range(loops):
        for key in keys:
            search(key)
    elapsed = time.perf_counter_ns() - start
    return elapsed / (loops * len(keys))


def loops_for(n):
    """Fewer loops for large arrays so the experiment finishes in reasonable time."""
    return max(1, 20_000 // n)


def run_case(table, array, keys, n):
    """Time one case in both structures. Returns a dict of results."""
    loops = loops_for(n)
    hash_runs = [time_searches(table.search, keys, loops) for _ in range(REPEATS)]
    array_runs = [time_searches(lambda k: linear_search(array, k), keys, loops)
                  for _ in range(REPEATS)]

    probes = statistics.mean(table.search_with_stats(k)[2] for k in keys)
    comparisons = statistics.mean(linear_search(array, k)[2] for k in keys)

    # check that both structures give the same answer for every key
    for k in keys:
        assert table.search(k) is linear_search(array, k)[0], f"mismatch for {k}"

    hash_ns = statistics.median(hash_runs)
    array_ns = statistics.median(array_runs)
    return {"hash_ns": hash_ns, "array_ns": array_ns,
            "speedup": array_ns / hash_ns,
            "probes": probes, "comparisons": comparisons}


def run_experiment(sizes):
    rows = []
    for n in sizes:
        products = generate_products(n)

        start = time.perf_counter()
        table, array = build_structures(products)
        build_s = time.perf_counter() - start

        rng = random.Random(SEED)
        ids = [p.product_id for p in products]
        cases = {
            "First": [ids[0]],
            "Middle": [ids[n // 2]],
            "Last": [ids[-1]],
            "Missing": ["X999999"],
            "Random": [rng.choice(ids) for _ in range(min(RANDOM_KEYS, n))],
        }

        print(f"\nDataset size n = {n:,}  (table capacity {table.capacity:,}, "
              f"load factor {table.load_factor:.2f}, collisions {table.collisions:,}, "
              f"build time {build_s:.3f} s)")
        print(f"{'Case':<9}{'Hash Table (ns)':>16}{'Array (ns)':>16}{'Speed-up':>11}"
              f"{'Avg probes':>12}{'Avg comparisons':>17}")
        print("-" * 81)

        for case, keys in cases.items():
            result = run_case(table, array, keys, n)
            print(f"{case:<9}{result['hash_ns']:>16,.0f}{result['array_ns']:>16,.0f}"
                  f"{result['speedup']:>10.1f}x{result['probes']:>12.2f}"
                  f"{result['comparisons']:>17,.1f}")
            rows.append({"n": n, "case": case, **result,
                         "load_factor": table.load_factor})
    return rows


# ---------------------------------------------------------------------- #
# Output
# ---------------------------------------------------------------------- #
def save_csv(rows, path="experiment_results.csv"):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nResults saved to {path}")


def save_chart(rows, path="experiment_chart.png"):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed - chart skipped (pip install matplotlib)")
        return

    random_rows = [r for r in rows if r["case"] == "Random"]
    sizes = [r["n"] for r in random_rows]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(sizes, [r["array_ns"] for r in random_rows], marker="o",
            label="1-D Array (linear search)")
    ax.plot(sizes, [r["hash_ns"] for r in random_rows], marker="s",
            label="Hash Table (linear probing)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Number of records (n)")
    ax.set_ylabel("Average time per search (ns, log scale)")
    ax.set_title("Search time vs dataset size (random existing keys)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    print(f"Chart saved to {path}")


def main():
    sizes = QUICK_SIZES if "--quick" in sys.argv else SIZES
    print("==== Search Performance Experiment: Hash Table vs 1-D Array ====")
    print(f"Python {platform.python_version()} | {platform.system()} {platform.release()} "
          f"| {platform.processor() or platform.machine()}")
    print(f"Timer: time.perf_counter_ns() | repeats per case: {REPEATS} (median reported) "
          f"| random seed: {SEED}")

    rows = run_experiment(sizes)
    save_csv(rows)
    save_chart(rows)


if __name__ == "__main__":
    main()