"""
main.py
-------
5022CMD Question 3: Fibonacci - Multithreading vs Sequential performance.

Runs:
  1. Environment information (for reproducibility).
  2. A warm-up round in each mode (not counted).
  3. The multithreaded experiment (one thread per Fibonacci number).
  4. The sequential experiment (same work, no threads).
  5. A summary comparison computed from the measured data.
  6. An I/O-bound demonstration showing when multithreading CAN help.
"""

import os
import platform
import sys
import time

from benchmark import (
    run_experiment,
    run_multithreaded_round,
    run_sequential_round,
    simulated_io_task,
    summarise,
)
from fibonacci import fibonacci, fibonacci_iterative

# ----------------------------- Configuration ------------------------------
FIB_INPUTS = (35, 38, 40)          # values required by the brief
ROUNDS = 10                        # number of measured rounds per mode
WARMUP_INPUTS = (20, 22, 25)       # small inputs for the uncounted warm-up round
IO_DELAYS_SECONDS = (1.0, 1.0, 1.0)
IO_ROUNDS = 3
NEGLIGIBLE_DIFFERENCE_PERCENT = 1.0   # below this, the difference is called "negligible"
LINE_WIDTH = 95


# ------------------------------ Formatting --------------------------------
def format_ns(value):
    """Format nanoseconds with thousands separators, e.g. 1,532,847,210 ns."""
    return f"{round(value):,} ns"


def print_heading(title):
    print()
    print("=" * LINE_WIDTH)
    print(title)
    print("=" * LINE_WIDTH)


def gil_status():
    """Describe whether the GIL is enabled (sys._is_gil_enabled exists from Python 3.13)."""
    if hasattr(sys, "_is_gil_enabled"):
        return "Enabled" if sys._is_gil_enabled() else "Disabled (free-threaded build)"
    return "Enabled (Python < 3.13 always has a GIL)"


def print_environment():
    clock = time.get_clock_info("perf_counter")
    print_heading("Test Environment")
    print(f"Python version  : {platform.python_version()} ({platform.python_implementation()})")
    print(f"GIL             : {gil_status()}")
    print(f"Operating system: {platform.platform()}")
    print(f"Logical CPUs    : {os.cpu_count()}")
    print(f"Timer           : time.perf_counter_ns() "
          f"(monotonic={clock.monotonic}, resolution={clock.resolution} s)")


def round_line(round_number, round_result, label_width):
    values = ", ".join(f"Fib({t.argument})={t.result}" for t in round_result.timings)
    return f"Round {round_number:>2} : {values} | T = {format_ns(round_result.elapsed_ns):>{label_width}}"


def print_timeline(round_result, title):
    """Optional item A: show each task's start/end relative to t1 (the first start)."""
    t1 = min(t.start_ns for t in round_result.timings)
    print(f"\n{title} (offsets relative to t1, the earliest start):")
    print(f"  {'Task':<10}{'Start offset':>22}{'End offset':>22}{'Duration':>22}")
    for t in round_result.timings:
        print(f"  {'Fib(' + str(t.argument) + ')':<10}"
              f"{format_ns(t.start_ns - t1):>22}"
              f"{format_ns(t.end_ns - t1):>22}"
              f"{format_ns(t.duration_ns):>22}")
    print(f"  T = t2 - t1 = {format_ns(round_result.elapsed_ns)}")


# ------------------------------ Experiments --------------------------------
def run_fibonacci_mode(title, round_function, fib_inputs, rounds, expected):
    """Run and print one experiment mode; return the list of T values (ns)."""
    print_heading(f"Fibonacci Computation ({title})")

    def show(round_number, round_result):
        print(round_line(round_number, round_result, 20), flush=True)

    round_results = run_experiment(round_function, fibonacci, fib_inputs, rounds,
                                   expected_results=expected, on_round_complete=show)
    times = [r.elapsed_ns for r in round_results]
    print(f"Average T ({title}) : {format_ns(summarise(times).mean_ns)}")
    print_timeline(round_results[0], f"Round 1 timeline - {title}")
    return times


def describe_change(threaded_mean, sequential_mean):
    """Build the observation sentence from the measured averages (never assumed)."""
    change_percent = (threaded_mean - sequential_mean) / sequential_mean * 100
    if abs(change_percent) < NEGLIGIBLE_DIFFERENCE_PERCENT:
        return (f"Multithreading made a negligible difference to the average completion "
                f"time ({change_percent:+.2f}%).")
    direction = "reduced" if change_percent < 0 else "increased"
    return (f"Multithreading {direction} the average completion time by "
            f"approximately {abs(change_percent):.2f}%.")


def print_summary(threaded_times, sequential_times, rounds):
    threaded = summarise(threaded_times)
    sequential = summarise(sequential_times)

    print_heading(f"Summary ({rounds} rounds each)")
    print(f"{'Metric':<20}{'With Multithreading':>30}{'Without Multithreading':>30}")
    print("-" * 80)
    for label, a, b in (
        ("Average T", threaded.mean_ns, sequential.mean_ns),
        ("Median T", threaded.median_ns, sequential.median_ns),
        ("Minimum T", threaded.min_ns, sequential.min_ns),
        ("Maximum T", threaded.max_ns, sequential.max_ns),
        ("Std deviation", threaded.stdev_ns, sequential.stdev_ns),
    ):
        print(f"{label:<20}{format_ns(a):>30}{format_ns(b):>30}")
    print("-" * 80)
    speedup = sequential.mean_ns / threaded.mean_ns
    print(f"Speed-up (sequential average / multithreaded average): {speedup:.3f}x")
    print(f"\nObservation: {describe_change(threaded.mean_ns, sequential.mean_ns)}")


def run_io_demo(delays, rounds):
    """Optional item C: an I/O-bound workload where multithreading is expected to help."""
    print_heading("Demonstration: I/O-bound tasks (simulated with time.sleep)")
    print(f"Each task waits {', '.join(f'{d}s' for d in delays)} - like waiting for downloads.\n")

    threaded, sequential = [], []
    for round_number in range(1, rounds + 1):
        threaded.append(run_multithreaded_round(simulated_io_task, delays).elapsed_ns)
        sequential.append(run_sequential_round(simulated_io_task, delays).elapsed_ns)
        print(f"Round {round_number}: With Multithreading T = {format_ns(threaded[-1]):>20} | "
              f"Without Multithreading T = {format_ns(sequential[-1]):>20}", flush=True)

    threaded_mean = summarise(threaded).mean_ns
    sequential_mean = summarise(sequential).mean_ns
    print(f"\nAverage T (With Multithreading)    : {format_ns(threaded_mean)}")
    print(f"Average T (Without Multithreading) : {format_ns(sequential_mean)}")
    print(f"Speed-up: {sequential_mean / threaded_mean:.3f}x")
    print(f"Observation: {describe_change(threaded_mean, sequential_mean)}")


# --------------------------------- Main -----------------------------------
def main(fib_inputs=FIB_INPUTS, rounds=ROUNDS, warmup_inputs=WARMUP_INPUTS,
         io_delays=IO_DELAYS_SECONDS, io_rounds=IO_ROUNDS):
    print_environment()

    # Expected answers from the independent O(n) version, used to verify every round.
    expected = tuple(fibonacci_iterative(n) for n in fib_inputs)

    # Optional item B: warm-up (not measured) so first-run effects do not affect round 1.
    run_multithreaded_round(fibonacci, warmup_inputs)
    run_sequential_round(fibonacci, warmup_inputs)

    threaded_times = run_fibonacci_mode("With Multithreading", run_multithreaded_round,
                                        fib_inputs, rounds, expected)
    sequential_times = run_fibonacci_mode("Without Multithreading", run_sequential_round,
                                          fib_inputs, rounds, expected)
    print_summary(threaded_times, sequential_times, rounds)

    if io_rounds > 0:
        run_io_demo(io_delays, io_rounds)


if __name__ == "__main__":
    main()
