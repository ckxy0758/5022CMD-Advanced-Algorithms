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
        self.graph.addVertex("A")
        self.assertTrue(self.graph.hasVertex("A"))
        self.assertEqual(self.graph.getVertices(), ["A"])

    def test_add_duplicate_vertex_raises_error(self):
        self.graph.addVertex("A")
        with self.assertRaises(ValueError):
            self.graph.addVertex("A")

    def test_graph_is_generic(self):
        # Works with any hashable type, not just strings (reusability).
        self.graph.addVertex(1)
        self.graph.addVertex(2)
        self.graph.addEdge(1, 2)
        self.assertEqual(self.graph.listIncomingAdjacentVertex(2), [1])

    def test_new_vertex_has_no_neighbours(self):
        self.graph.addVertex("A")
        self.assertEqual(self.graph.listIncomingAdjacentVertex("A"), [])
        self.assertEqual(self.graph.listOutgoingAdjacentVertex("A"), [])


class TestEdgeOperations(unittest.TestCase):

    def setUp(self):
        # A -> B, A -> C, B -> C
        self.graph = DirectedGraph()
        for vertex in ("A", "B", "C"):
            self.graph.addVertex(vertex)
        self.graph.addEdge("A", "B")
        self.graph.addEdge("A", "C")
        self.graph.addEdge("B", "C")

    def test_edge_is_directed(self):
        self.assertTrue(self.graph.hasEdge("A", "B"))
        self.assertFalse(self.graph.hasEdge("B", "A"))

    def test_list_incoming_adjacent_vertex(self):
        self.assertEqual(self.graph.listIncomingAdjacentVertex("C"), ["A", "B"])
        self.assertEqual(self.graph.listIncomingAdjacentVertex("A"), [])

    def test_list_outgoing_adjacent_vertex(self):
        self.assertEqual(self.graph.listOutgoingAdjacentVertex("A"), ["B", "C"])
        self.assertEqual(self.graph.listOutgoingAdjacentVertex("C"), [])

    def test_get_edges(self):
        self.assertEqual(self.graph.getEdges(), [("A", "B"), ("A", "C"), ("B", "C")])

    def test_add_edge_with_missing_vertex_raises_error(self):
        with self.assertRaises(ValueError):
            self.graph.addEdge("A", "Z")
        with self.assertRaises(ValueError):
            self.graph.addEdge("Z", "A")

    def test_self_loop_raises_error(self):
        with self.assertRaises(ValueError):
            self.graph.addEdge("A", "A")

    def test_duplicate_edge_raises_error(self):
        with self.assertRaises(ValueError):
            self.graph.addEdge("A", "B")

    def test_remove_edge_updates_both_directions(self):
        self.graph.removeEdge("A", "C")
        self.assertFalse(self.graph.hasEdge("A", "C"))
        self.assertEqual(self.graph.listOutgoingAdjacentVertex("A"), ["B"])
        self.assertEqual(self.graph.listIncomingAdjacentVertex("C"), ["B"])

    def test_remove_missing_edge_raises_error(self):
        with self.assertRaises(ValueError):
            self.graph.removeEdge("C", "A")

    def test_returned_list_is_a_copy(self):
        # Changing the returned list must NOT change the graph (encapsulation).
        incoming = self.graph.listIncomingAdjacentVertex("C")
        incoming.append("X")
        self.assertEqual(self.graph.listIncomingAdjacentVertex("C"), ["A", "B"])

    def test_query_missing_vertex_raises_error(self):
        with self.assertRaises(ValueError):
            self.graph.listIncomingAdjacentVertex("Z")


class TestHasPath(unittest.TestCase):

    def setUp(self):
        # A -> B -> C,   D is isolated
        self.graph = DirectedGraph()
        for vertex in ("A", "B", "C", "D"):
            self.graph.addVertex(vertex)
        self.graph.addEdge("A", "B")
        self.graph.addEdge("B", "C")

    def test_direct_path(self):
        self.assertTrue(self.graph.hasPath("A", "B"))

    def test_indirect_path(self):
        self.assertTrue(self.graph.hasPath("A", "C"))

    def test_path_respects_direction(self):
        self.assertFalse(self.graph.hasPath("C", "A"))

    def test_no_path_to_isolated_vertex(self):
        self.assertFalse(self.graph.hasPath("A", "D"))

    def test_vertex_reaches_itself(self):
        self.assertTrue(self.graph.hasPath("A", "A"))


if __name__ == "__main__":
    unittest.main()