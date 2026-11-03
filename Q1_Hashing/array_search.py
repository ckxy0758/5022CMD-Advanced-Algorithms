"""
Linear search on a one-dimensional array (Python list).
Used for comparison with the hash table (Question 1, Task 4).
"""


def linear_search(array, product_id):
    """Check each element from index 0 until the ID matches.

    Returns (product, index, comparisons). product and index are None if absent.
    Time complexity: O(n) - in the worst case every element is checked.
    """
    comparisons = 0
    for index, product in enumerate(array):
        comparisons += 1
        if product.product_id == product_id:
            return product, index, comparisons
    return None, None, comparisons