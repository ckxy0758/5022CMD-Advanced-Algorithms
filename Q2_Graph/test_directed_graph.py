"""
Unit tests for the generic DirectedGraph class.

Run from the Q2_CourseGraph folder:
    python -m unittest discover -v
"""

import unittest

from directed_graph import DirectedGraph


class TestVertexOperations(unittest.TestCase):

    def setUp(self):
        self.graph = DirectedGraph()

    def test_add_vertex(self):
        self.graph.add_vertex("A")
        self.assertTrue(self.graph.has_vertex("A"))
        self.assertEqual(self.graph.get_vertices(), ["A"])

    def test_add_duplicate_vertex_raises_error(self):
        self.graph.add_vertex("A")
        with self.assertRaises(ValueError):
            self.graph.add_vertex("A")

    def test_graph_is_generic(self):
        # Works with any hashable type, not just strings (reusability).
        self.graph.add_vertex(1)
        self.graph.add_vertex(2)
        self.graph.add_edge(1, 2)
        self.assertEqual(self.graph.list_incoming_adjacent_vertex(2), [1])

    def test_new_vertex_has_no_neighbours(self):
        self.graph.add_vertex("A")
        self.assertEqual(self.graph.list_incoming_adjacent_vertex("A"), [])
        self.assertEqual(self.graph.list_outgoing_adjacent_vertex("A"), [])


class TestEdgeOperations(unittest.TestCase):

    def setUp(self):
        # A -> B, A -> C, B -> C
        self.graph = DirectedGraph()
        for vertex in ("A", "B", "C"):
            self.graph.add_vertex(vertex)
        self.graph.add_edge("A", "B")
        self.graph.add_edge("A", "C")
        self.graph.add_edge("B", "C")

    def test_edge_is_directed(self):
        self.assertTrue(self.graph.has_edge("A", "B"))
        self.assertFalse(self.graph.has_edge("B", "A"))

    def test_list_incoming_adjacent_vertex(self):
        self.assertEqual(self.graph.list_incoming_adjacent_vertex("C"), ["A", "B"])
        self.assertEqual(self.graph.list_incoming_adjacent_vertex("A"), [])

    def test_list_outgoing_adjacent_vertex(self):
        self.assertEqual(self.graph.list_outgoing_adjacent_vertex("A"), ["B", "C"])
        self.assertEqual(self.graph.list_outgoing_adjacent_vertex("C"), [])

    def test_get_edges(self):
        self.assertEqual(self.graph.get_edges(), [("A", "B"), ("A", "C"), ("B", "C")])

    def test_add_edge_with_missing_vertex_raises_error(self):
        with self.assertRaises(ValueError):
            self.graph.add_edge("A", "Z")
        with self.assertRaises(ValueError):
            self.graph.add_edge("Z", "A")

    def test_self_loop_raises_error(self):
        with self.assertRaises(ValueError):
            self.graph.add_edge("A", "A")

    def test_duplicate_edge_raises_error(self):
        with self.assertRaises(ValueError):
            self.graph.add_edge("A", "B")

    def test_remove_edge_updates_both_directions(self):
        self.graph.remove_edge("A", "C")
        self.assertFalse(self.graph.has_edge("A", "C"))
        self.assertEqual(self.graph.list_outgoing_adjacent_vertex("A"), ["B"])
        self.assertEqual(self.graph.list_incoming_adjacent_vertex("C"), ["B"])

    def test_remove_missing_edge_raises_error(self):
        with self.assertRaises(ValueError):
            self.graph.remove_edge("C", "A")

    def test_returned_list_is_a_copy(self):
        # Changing the returned list must NOT change the graph (encapsulation).
        incoming = self.graph.list_incoming_adjacent_vertex("C")
        incoming.append("X")
        self.assertEqual(self.graph.list_incoming_adjacent_vertex("C"), ["A", "B"])

    def test_query_missing_vertex_raises_error(self):
        with self.assertRaises(ValueError):
            self.graph.list_incoming_adjacent_vertex("Z")


class TestHasPath(unittest.TestCase):

    def setUp(self):
        # A -> B -> C,   D is isolated
        self.graph = DirectedGraph()
        for vertex in ("A", "B", "C", "D"):
            self.graph.add_vertex(vertex)
        self.graph.add_edge("A", "B")
        self.graph.add_edge("B", "C")

    def test_direct_path(self):
        self.assertTrue(self.graph.has_path("A", "B"))

    def test_indirect_path(self):
        self.assertTrue(self.graph.has_path("A", "C"))

    def test_path_respects_direction(self):
        self.assertFalse(self.graph.has_path("C", "A"))

    def test_no_path_to_isolated_vertex(self):
        self.assertFalse(self.graph.has_path("A", "D"))

    def test_vertex_reaches_itself(self):
        self.assertTrue(self.graph.has_path("A", "A"))


if __name__ == "__main__":
    unittest.main()