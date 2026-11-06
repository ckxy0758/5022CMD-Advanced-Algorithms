"""
benchmark.py
------------
Reusable timing tools for comparing multithreaded and sequential execution.

The functions here are generic: they accept ANY task function and a list of
arguments, so the same code measures the Fibonacci workload and the I/O demo.

Timing rule (from the assignment brief), used for BOTH modes:
    T = End_Time_Of_Task_Finished_Last - Start_Time_Of_Task_That_Started_First
All timestamps come from time.perf_counter_ns() (monotonic, integer nanoseconds).
"""

import statistics
import threading
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class TaskTiming:
    """Result and start/end timestamps (ns) of one task, e.g. Fib(35)."""
    argument: object
    result: object
    start_ns: int
    end_ns: int

    @property
    def duration_ns(self):
        return self.end_ns - self.start_ns


@dataclass(frozen=True)
class RoundResult:
    """All task timings from one round, kept in the same order as the arguments."""
    timings: tuple

    @property
    def results(self):
        return tuple(timing.result for timing in self.timings)

    @property
    def elapsed_ns(self):
        """T = end of the task that finished last - start of the task that started first."""
        first_start = min(timing.start_ns for timing in self.timings)
        last_end = max(timing.end_ns for timing in self.timings)
        return last_end - first_start


@dataclass(frozen=True)
class Summary:
    """Descriptive statistics (ns) for the T values of several rounds."""
    mean_ns: float
    median_ns: float      # middle value: not pulled up by a single outlier round
    min_ns: int
    max_ns: int
    stdev_ns: float


class TaskThread(threading.Thread):
    """
    A thread that runs task(argument) and records its own start and end time.

    Data consistency: each thread writes ONLY its own attributes (timing, error),
    and the main thread reads them only AFTER join(). No variable is shared for
    writing, so there is no race condition and no lock is needed.
    """

    def __init__(self, task, argument):
        super().__init__(name=f"{task.__name__}({argument})")
        self._task = task
        self._argument = argument
        self.timing = None
        self.error = None

    def run(self):
        start_ns = time.perf_counter_ns()
        try:
            result = self._task(self._argument)
        except Exception as exc:          # store the error so the main thread can report it
            self.error = exc
            return
        end_ns = time.perf_counter_ns()
        self.timing = TaskTiming(self._argument, result, start_ns, end_ns)


def run_multithreaded_round(task, arguments):
    """Run task(arg) for every argument, ONE separate thread per argument."""
    threads = [TaskThread(task, argument) for argument in arguments]

    for thread in threads:      # start all threads
        thread.start()
    for thread in threads:      # wait until every thread has finished
        thread.join()

    for thread in threads:      # a thread that crashed must not be silently ignored
        if thread.error is not None:
            raise RuntimeError(f"Thread {thread.name} failed") from thread.error

    return RoundResult(tuple(thread.timing for thread in threads))


def run_sequential_round(task, arguments):
    """Run task(arg) for every argument, one after another in the main thread."""
    timings = []
    for argument in arguments:
        start_ns = time.perf_counter_ns()
        result = task(argument)
        end_ns = time.perf_counter_ns()
        timings.append(TaskTiming(argument, result, start_ns, end_ns))
    return RoundResult(tuple(timings))


def run_experiment(round_function, task, arguments, rounds,
                   expected_results=None, on_round_complete=None):
    """
    Repeat one round function several times and return the list of RoundResults.

    expected_results  : if given, every round's results are checked against it
                        (done AFTER timing, so checking does not affect T).
    on_round_complete : optional callback(round_number, round_result), used by
                        main.py to print each round as soon as it finishes.
    """
    if rounds < 1:
        raise ValueError("rounds must be at least 1")

    round_results = []
    for round_number in range(1, rounds + 1):
        round_result = round_function(task, arguments)

        if expected_results is not None and round_result.results != tuple(expected_results):
            raise AssertionError(
                f"Round {round_number}: got {round_result.results}, "
                f"expected {tuple(expected_results)}"
            )

        round_results.append(round_result)
        if on_round_complete is not None:
            on_round_complete(round_number, round_result)

    return round_results


def summarise(times_ns):
    """Return mean, median, minimum, maximum and sample standard deviation of T values."""
    if not times_ns:
        raise ValueError("times_ns must not be empty")
    stdev = statistics.stdev(times_ns) if len(times_ns) > 1 else 0.0
    return Summary(statistics.mean(times_ns), statistics.median(times_ns),
                   min(times_ns), max(times_ns), stdev)


def simulated_io_task(seconds):
    """
    Simulate an I/O-bound task (e.g. waiting for a download) by sleeping.
    While sleeping, a thread releases the GIL, so other threads can run.
    """
    time.sleep(seconds)
    return seconds
