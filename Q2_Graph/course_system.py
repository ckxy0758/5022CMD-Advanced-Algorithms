"""
course_system.py

The Course Prerequisite System: connects Course objects (course.py) with the
generic DirectedGraph (directed_graph.py) and enforces the domain rules.

Edge direction convention:
    prerequisite  ->  course
e.g. CS101 -> CS201 means "CS101 is a prerequisite of CS201".
So, for a course X:
    incoming edges of X = prerequisites of X
    outgoing edges of X = courses unlocked by X
"""

from course import Course
from directed_graph import DirectedGraph


class CoursePrerequisiteSystem:
    """Stores courses and their prerequisite relationships.

    _courses : dict  course code -> Course object   (O(1) lookup by code)
    _graph   : DirectedGraph whose vertices are course codes (strings)
    Both structures are always updated together so they stay consistent.
    """

    DEFAULT_MAX_COURSES = 10   # brief: maximum of 10 courses

    def __init__(self, max_courses: int = DEFAULT_MAX_COURSES):
        self._courses = {}
        self._graph = DirectedGraph()
        self._max_courses = max_courses

    # ------------------------------------------------------------------
    # Course operations
    # ------------------------------------------------------------------
    def add_course(self, course: Course) -> None:
        """Add a new course (creates a new vertex in the graph).

        All checks happen BEFORE anything is changed, so a failed add never
        leaves the dictionary and the graph out of sync.
        """
        if not isinstance(course, Course):
            raise ValueError("Only Course objects can be added.")
        if len(self._courses) >= self._max_courses:
            raise ValueError(f"Cannot add more than {self._max_courses} courses.")
        code = course.get_course_code()
        if code in self._courses:
            raise ValueError(f"Course code '{code}' already exists.")

        self._graph.addVertex(code)
        self._courses[code] = course

    def has_course(self, code: str) -> bool:
        return self._normalise_code(code) in self._courses

    def get_course(self, code: str) -> Course:
        """Return the Course with this code (case-insensitive). Time: O(1)."""
        normalised = self._normalise_code(code)
        if normalised not in self._courses:
            raise ValueError(f"Course '{normalised}' does not exist.")
        return self._courses[normalised]

    def get_all_courses(self) -> list:
        """Return all courses in the order they were added. Time: O(V)."""
        return list(self._courses.values())

    def get_course_count(self) -> int:
        return len(self._courses)

    def get_max_courses(self) -> int:
        return self._max_courses

    # ------------------------------------------------------------------
    # Prerequisite queries
    # ------------------------------------------------------------------
    def get_prerequisites(self, code: str) -> list:
        """Courses required BEFORE this course (incoming edges). Time: O(in-degree)."""
        course = self.get_course(code)
        codes = self._graph.listIncomingAdjacentVertex(course.get_course_code())
        return [self._courses[c] for c in codes]

    def get_unlocked_courses(self, code: str) -> list:
        """Courses this course is a prerequisite for (outgoing edges). Time: O(out-degree)."""
        course = self.get_course(code)
        codes = self._graph.list_outgoing_adjacent_vertex(course.get_course_code())
        return [self._courses[c] for c in codes]

    # ------------------------------------------------------------------
    # Prerequisite updates
    # ------------------------------------------------------------------
    def add_prerequisite(self, course_code: str, prerequisite_code: str) -> None:
        """Make prerequisite_code (Y) a prerequisite of course_code (X): adds edge Y -> X.

        Rejected if: either course is missing, X == Y, the link already exists,
        or the new edge would create a cycle.
        Cycle rule: adding Y -> X creates a cycle if X can ALREADY reach Y
        (X -> ... -> Y), because Y -> X would then close the loop.
        Time: O(V + E) because of the DFS in has_path.
        """
        course = self.get_course(course_code).get_course_code()
        prerequisite = self.get_course(prerequisite_code).get_course_code()

        if course == prerequisite:
            raise ValueError("A course cannot be a prerequisite of itself.")
        if self._graph.has_edge(prerequisite, course):
            raise ValueError(f"{prerequisite} is already a prerequisite of {course}.")
        if self._graph.has_path(course, prerequisite):
            raise ValueError(f"Cannot add {prerequisite} as a prerequisite of {course}: "
                             f"{course} is already required (directly or indirectly) "
                             f"before {prerequisite}, so this would create a cycle.")

        self._graph.addEdge(prerequisite, course)

    def remove_prerequisite(self, course_code: str, prerequisite_code: str) -> None:
        """Remove prerequisite_code (Y) from course_code (X): removes edge Y -> X."""
        course = self.get_course(course_code).get_course_code()
        prerequisite = self.get_course(prerequisite_code).get_course_code()

        if not self._graph.has_edge(prerequisite, course):
            raise ValueError(f"{prerequisite} is not a direct prerequisite of {course}.")
        self._graph.remove_edge(prerequisite, course)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def get_graph_as_text(self) -> str:
        """Adjacency-list view of the graph (prerequisite -> unlocked courses)."""
        return str(self._graph)

    @staticmethod
    def _normalise_code(code) -> str:
        """Make user input consistent: ' cs201 ' -> 'CS201'."""
        if not isinstance(code, str):
            raise ValueError("Course code must be text.")
        return code.strip().upper()