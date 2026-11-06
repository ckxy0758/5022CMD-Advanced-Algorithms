"""
fibonacci.py
------------
Fibonacci functions for 5022CMD Question 3 (Concurrent Process).

fibonacci(n)            - naive recursive version (the function analysed for Big-O
                          and used as the CPU-bound workload in the experiment).
fibonacci_iterative(n)  - fast O(n) reference version, used ONLY to verify that the
                          recursive results are correct (an independent "oracle").
"""


def _validate(n):
    """Raise an error if n is not a non-negative integer."""
    # bool is a subclass of int in Python (True == 1), so reject it explicitly.
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError(f"n must be an integer, got {type(n).__name__}")
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")


def _fib(n):
    """
    Recursive core: F(0) = 0, F(1) = 1, F(n) = F(n-1) + F(n-2).

    Time complexity : O(2^n) upper bound, tight bound Theta(phi^n), phi ~ 1.618
    Space complexity: O(n)  (maximum depth of the recursion)
    """
    if n <= 1:                         # base case: F(0) = 0, F(1) = 1
        return n
    return _fib(n - 1) + _fib(n - 2)   # two recursive calls per non-base call


def fibonacci(n):
    """
    Return the nth Fibonacci number using naive recursion.

    Input is validated once here, so the recursive core (_fib) does no extra
    checking on every call. This keeps the primitive-operation count per call
    small and constant.
    """
    _validate(n)
    return _fib(n)


def fibonacci_iterative(n):
    """Return the nth Fibonacci number in O(n) time (used for verification only)."""
    _validate(n)
    previous, current = 0, 1
    for _ in range(n):
        previous, current = current, previous + current
    return previous
