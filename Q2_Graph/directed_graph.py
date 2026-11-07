"""
directed_graph.py

A generic, reusable UNWEIGHTED DIRECTED graph using an adjacency-list
representation built on Python dictionaries.

This module contains NO course-specific code. A vertex can be any hashable
value (e.g. str, int, tuple), so the class can be reused in other contexts
such as road maps, web links or task dependencies.
"""

from collections.abc import Hashable


class DirectedGraph:
    """An unweighted directed graph stored as two adjacency-list dictionaries.

    _outgoing[v] -> list of vertices that v points TO     (edges v -> w)
    _incoming[v] -> list of vertices that point TO v      (edges u -> v)

    Every edge is stored twice (once in each dictionary). This costs extra
    memory, but lets us list BOTH the incoming and the outgoing neighbours of
    a vertex in O(degree) time, instead of scanning the whole graph, O(V + E).
    """

    def __init__(self):
        self._outgoing = {}  # vertex -> list of successor vertices
        self._incoming = {}  # vertex -> list of predecessor vertices

    # ------------------------------------------------------------------
    # Vertex operations
    # ------------------------------------------------------------------
    def addVertex(self, vertex: Hashable) -> None:
        """Add a new vertex with no edges.

        Raises ValueError if the vertex already exists, so existing edges
        are never overwritten by accident.  Time: O(1) average.
        """
        if vertex in self._outgoing:
            raise ValueError(f"Vertex '{vertex}' already exists in the graph.")
        self._outgoing[vertex] = []
        self._incoming[vertex] = []

    def has_vertex(self, vertex: Hashable) -> bool:
        """Return True if the vertex exists.  Time: O(1) average."""
        return vertex in self._outgoing

    def get_vertices(self) -> list:
        """Return all vertices (in insertion order).  Time: O(V)."""
        return list(self._outgoing)

    # ------------------------------------------------------------------
    # Edge operations
    # ------------------------------------------------------------------
    def addEdge(self, from_vertex: Hashable, to_vertex: Hashable) -> None:
        """Add a directed edge from_vertex -> to_vertex.

        Rules (keep the graph a "simple graph", as defined in Chapter 5):
          * both vertices must already exist
          * no self-loop (a vertex cannot point to itself)
          * no duplicate edge
        Time: O(1) average + O(out-degree) for the duplicate check.
        """
        self._require_vertex(from_vertex)
        self._require_vertex(to_vertex)
        if from_vertex == to_vertex:
            raise ValueError(f"Self-loop on '{from_vertex}' is not allowed.")
        if self.has_edge(from_vertex, to_vertex):
            raise ValueError(f"Edge '{from_vertex}' -> '{to_vertex}' already exists.")

        # Update BOTH dictionaries so they always stay consistent.
        self._outgoing[from_vertex].append(to_vertex)
        self._incoming[to_vertex].append(from_vertex)

    def remove_edge(self, from_vertex: Hashable, to_vertex: Hashable) -> None:
        """Remove the directed edge from_vertex -> to_vertex.

        Raises ValueError if the edge does not exist.  Time: O(degree).
        """
        if not self.has_edge(from_vertex, to_vertex):
            raise ValueError(f"Edge '{from_vertex}' -> '{to_vertex}' does not exist.")
        self._outgoing[from_vertex].remove(to_vertex)
        self._incoming[to_vertex].remove(from_vertex)

    def has_edge(self, from_vertex: Hashable, to_vertex: Hashable) -> bool:
        """Return True if the edge from_vertex -> to_vertex exists.  Time: O(out-degree)."""
        return from_vertex in self._outgoing and to_vertex in self._outgoing[from_vertex]

    def get_edges(self) -> list:
        """Return every edge as a (from_vertex, to_vertex) tuple.  Time: O(V + E)."""
        return [(source, target)
                for source, targets in self._outgoing.items()
                for target in targets]

    # ------------------------------------------------------------------
    # Neighbour queries
    # ------------------------------------------------------------------
    def listIncomingAdjacentVertex(self, vertex: Hashable) -> list:
        """Return all vertices that have an edge INTO the given vertex.

        A copy is returned so callers cannot modify the graph's internal
        data by accident.  Time: O(in-degree).
        """
        self._require_vertex(vertex)
        return list(self._incoming[vertex])

    def list_outgoing_adjacent_vertex(self, vertex: Hashable) -> list:
        """Return all vertices that the given vertex has an edge TO.

        Returns a copy.  Time: O(out-degree).
        """
        self._require_vertex(vertex)
        return list(self._outgoing[vertex])

    # ------------------------------------------------------------------
    # Traversal
    # ------------------------------------------------------------------
    def has_path(self, start: Hashable, target: Hashable) -> bool:
        """Return True if target can be reached from start by following edges.

        Uses an iterative Depth-First Search (DFS, Chapter 5) with an explicit
        stack and a visited set. A vertex is marked as visited when it is
        pushed, so each vertex enters the stack at most once.
        A vertex is always considered reachable from itself.
        Time: O(V + E).  Space: O(V).
        """
        self._require_vertex(start)
        self._require_vertex(target)

        visited = {start}
        stack = [start]
        while stack:
            current = stack.pop()            # LIFO -> depth-first
            if current == target:
                return True
            for neighbour in self._outgoing[current]:
                if neighbour not in visited:
                    visited.add(neighbour)   # mark on push -> pushed at most once
                    stack.append(neighbour)
        return False

    # ------------------------------------------------------------------
    # Display and helpers
    # ------------------------------------------------------------------
    def __str__(self) -> str:
        """Show the graph as an adjacency list, one vertex per line."""
        if not self._outgoing:
            return "(empty graph)"
        return "\n".join(f"{vertex} -> {targets}"
                         for vertex, targets in self._outgoing.items())

    def _require_vertex(self, vertex: Hashable) -> None:
        """Raise ValueError if the vertex is not in the graph (internal helper)."""
        if vertex not in self._outgoing:
            raise ValueError(f"Vertex '{vertex}' does not exist in the graph.")