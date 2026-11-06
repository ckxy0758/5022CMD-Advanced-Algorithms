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

    def hasVertex(self, vertex: Hashable) -> bool:
        """Return True if the vertex exists.  Time: O(1) average."""
        return vertex in self._outgoing

    def getVertices(self) -> list:
        """Return all vertices (in insertion order).  Time: O(V)."""
        return list(self._outgoing)

    # ------------------------------------------------------------------
    # Edge operations
    # ------------------------------------------------------------------
    def addEdge(self, fromVertex: Hashable, toVertex: Hashable) -> None:
        """Add a directed edge fromVertex -> toVertex.

        Rules (keep the graph a "simple graph", as defined in Chapter 5):
          * both vertices must already exist
          * no self-loop (a vertex cannot point to itself)
          * no duplicate edge
        Time: O(1) average + O(out-degree) for the duplicate check.
        """
        self._requireVertex(fromVertex)
        self._requireVertex(toVertex)
        if fromVertex == toVertex:
            raise ValueError(f"Self-loop on '{fromVertex}' is not allowed.")
        if self.hasEdge(fromVertex, toVertex):
            raise ValueError(f"Edge '{fromVertex}' -> '{toVertex}' already exists.")

        # Update BOTH dictionaries so they always stay consistent.
        self._outgoing[fromVertex].append(toVertex)
        self._incoming[toVertex].append(fromVertex)

    def removeEdge(self, fromVertex: Hashable, toVertex: Hashable) -> None:
        """Remove the directed edge fromVertex -> toVertex.

        Raises ValueError if the edge does not exist.  Time: O(degree).
        """
        if not self.hasEdge(fromVertex, toVertex):
            raise ValueError(f"Edge '{fromVertex}' -> '{toVertex}' does not exist.")
        self._outgoing[fromVertex].remove(toVertex)
        self._incoming[toVertex].remove(fromVertex)

    def hasEdge(self, fromVertex: Hashable, toVertex: Hashable) -> bool:
        """Return True if the edge fromVertex -> toVertex exists.  Time: O(out-degree)."""
        return fromVertex in self._outgoing and toVertex in self._outgoing[fromVertex]

    def getEdges(self) -> list:
        """Return every edge as a (fromVertex, toVertex) tuple.  Time: O(V + E)."""
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
        self._requireVertex(vertex)
        return list(self._incoming[vertex])

    def listOutgoingAdjacentVertex(self, vertex: Hashable) -> list:
        """Return all vertices that the given vertex has an edge TO.

        Returns a copy.  Time: O(out-degree).
        """
        self._requireVertex(vertex)
        return list(self._outgoing[vertex])

    # ------------------------------------------------------------------
    # Traversal
    # ------------------------------------------------------------------
    def hasPath(self, start: Hashable, target: Hashable) -> bool:
        """Return True if target can be reached from start by following edges.

        Uses an iterative Depth-First Search (DFS, Chapter 5) with an explicit
        stack and a visited set, so each vertex is processed at most once.
        A vertex is always considered reachable from itself.
        Time: O(V + E).  Space: O(V).
        """
        self._requireVertex(start)
        self._requireVertex(target)

        visited = set()
        stack = [start]
        while stack:
            current = stack.pop()            # LIFO -> depth-first
            if current == target:
                return True
            if current in visited:
                continue
            visited.add(current)
            for neighbour in self._outgoing[current]:
                if neighbour not in visited:
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

    def _requireVertex(self, vertex: Hashable) -> None:
        """Raise ValueError if the vertex is not in the graph (internal helper)."""
        if vertex not in self._outgoing:
            raise ValueError(f"Vertex '{vertex}' does not exist in the graph.")