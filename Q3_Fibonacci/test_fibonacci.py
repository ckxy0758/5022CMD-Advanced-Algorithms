"""
test_fibonacci.py
-----------------
Unit tests for Question 3. Run with:  python -m unittest test_fibonacci -v

Small inputs are used so the tests finish quickly.
"""

import unittest

from benchmark import (
    run_experiment,
    run_multithreaded_round,
    run_sequential_round,
    summarise,
)
from fibonacci import fibonacci, fibonacci_iterative

SMALL_INPUTS = (10, 15, 20)


class TestFibonacci(unittest.TestCase):

    def test_base_cases(self):
        self.assertEqual(fibonacci(0), 0)
        self.assertEqual(fibonacci(1), 1)

    def test_known_values(self):
        known = {2: 1, 3: 2, 5: 5, 10: 55, 20: 6765}
        for n, value in known.items():
            self.assertEqual(fibonacci(n), value, f"F({n})")

    def test_recursive_matches_iterative(self):
        for n in range(25):
            self.assertEqual(fibonacci(n), fibonacci_iterative(n), f"F({n})")

    def test_iterative_brief_values(self):
        # Values required by the brief (checked with the fast version).
        self.assertEqual(fibonacci_iterative(35), 9227465)
        self.assertEqual(fibonacci_iterative(38), 39088169)
        self.assertEqual(fibonacci_iterative(40), 102334155)

    def test_negative_input_rejected(self):
        for function in (fibonacci, fibonacci_iterative):
            with self.assertRaises(ValueError):
                function(-1)

    def test_non_integer_input_rejected(self):
        for function in (fibonacci, fibonacci_iterative):
            for bad in (3.5, "10", None, True):
                with self.assertRaises(TypeError):
                    function(bad)


class TestBenchmark(unittest.TestCase):

    def setUp(self):
        self.expected = tuple(fibonacci_iterative(n) for n in SMALL_INPUTS)

    def test_both_modes_give_correct_results_in_order(self):
        for round_function in (run_multithreaded_round, run_sequential_round):
            result = round_function(fibonacci, SMALL_INPUTS)
            self.assertEqual(result.results, self.expected)
            self.assertEqual(tuple(t.argument for t in result.timings), SMALL_INPUTS)

    def test_elapsed_time_follows_brief_formula(self):
        for round_function in (run_multithreaded_round, run_sequential_round):
            result = round_function(fibonacci, SMALL_INPUTS)
            first_start = min(t.start_ns for t in result.timings)
            last_end = max(t.end_ns for t in result.timings)
            self.assertEqual(result.elapsed_ns, last_end - first_start)
            self.assertGreater(result.elapsed_ns, 0)
            # T can never be shorter than the longest single task.
            self.assertGreaterEqual(result.elapsed_ns,
                                    max(t.duration_ns for t in result.timings))

    def test_one_thread_per_argument(self):
        result = run_multithreaded_round(fibonacci, SMALL_INPUTS)
        self.assertEqual(len(result.timings), len(SMALL_INPUTS))

    def test_run_experiment_returns_each_round(self):
        results = run_experiment(run_sequential_round, fibonacci, SMALL_INPUTS, 3,
                                 expected_results=self.expected)
        self.assertEqual(len(results), 3)

    def test_run_experiment_detects_wrong_results(self):
        with self.assertRaises(AssertionError):
            run_experiment(run_sequential_round, fibonacci, SMALL_INPUTS, 1,
                           expected_results=(0, 0, 0))

    def test_run_experiment_rejects_zero_rounds(self):
        with self.assertRaises(ValueError):
            run_experiment(run_sequential_round, fibonacci, SMALL_INPUTS, 0)

    def test_thread_error_is_reported(self):
        with self.assertRaises(RuntimeError):
            run_multithreaded_round(fibonacci, (5, -1, 7))

    def test_summarise(self):
        summary = summarise([1, 2, 3])
        self.assertEqual((summary.mean_ns, summary.min_ns, summary.max_ns), (2, 1, 3))
        self.assertAlmostEqual(summary.stdev_ns, 1.0)
        self.assertEqual(summarise([5]).stdev_ns, 0.0)
        # The median ignores one extreme outlier, while the mean is pulled up by it.
        with_outlier = summarise([10, 11, 12, 13, 100])
        self.assertEqual(with_outlier.median_ns, 12)
        self.assertEqual(with_outlier.mean_ns, 29.2)
        with self.assertRaises(ValueError):
            summarise([])


if __name__ == "__main__":
    unittest.main(verbosity=2)
