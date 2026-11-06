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

    def __init__(self, maxCourses: int = DEFAULT_MAX_COURSES):
        self._courses = {}
        self._graph = DirectedGraph()
        self._maxCourses = maxCourses

    # ------------------------------------------------------------------
    # Course operations
    # ------------------------------------------------------------------
    def addCourse(self, course: Course) -> None:
        """Add a new course (creates a new vertex in the graph).

        All checks happen BEFORE anything is changed, so a failed add never
        leaves the dictionary and the graph out of sync.
        """
        if not isinstance(course, Course):
            raise ValueError("Only Course objects can be added.")
        if len(self._courses) >= self._maxCourses:
            raise ValueError(f"Cannot add more than {self._maxCourses} courses.")
        code = course.getCourseCode()
        if code in self._courses:
            raise ValueError(f"Course code '{code}' already exists.")

        self._graph.addVertex(code)
        self._courses[code] = course

    def hasCourse(self, code: str) -> bool:
        return self._normaliseCode(code) in self._courses

    def getCourse(self, code: str) -> Course:
        """Return the Course with this code (case-insensitive). Time: O(1)."""
        normalised = self._normaliseCode(code)
        if normalised not in self._courses:
            raise ValueError(f"Course '{normalised}' does not exist.")
        return self._courses[normalised]

    def getAllCourses(self) -> list:
        """Return all courses in the order they were added. Time: O(V)."""
        return list(self._courses.values())

    def getCourseCount(self) -> int:
        return len(self._courses)

    def getMaxCourses(self) -> int:
        return self._maxCourses

    # ------------------------------------------------------------------
    # Prerequisite queries
    # ------------------------------------------------------------------
    def getPrerequisites(self, code: str) -> list:
        """Courses required BEFORE this course (incoming edges). Time: O(in-degree)."""
        course = self.getCourse(code)
        codes = self._graph.listIncomingAdjacentVertex(course.getCourseCode())
        return [self._courses[c] for c in codes]

    def getUnlockedCourses(self, code: str) -> list:
        """Courses this course is a prerequisite for (outgoing edges). Time: O(out-degree)."""
        course = self.getCourse(code)
        codes = self._graph.listOutgoingAdjacentVertex(course.getCourseCode())
        return [self._courses[c] for c in codes]

    # ------------------------------------------------------------------
    # Prerequisite updates
    # ------------------------------------------------------------------
    def addPrerequisite(self, courseCode: str, prerequisiteCode: str) -> None:
        """Make prerequisiteCode (Y) a prerequisite of courseCode (X): adds edge Y -> X.

        Rejected if: either course is missing, X == Y, the link already exists,
        or the new edge would create a cycle.
        Cycle rule: adding Y -> X creates a cycle if X can ALREADY reach Y
        (X -> ... -> Y), because Y -> X would then close the loop.
        Time: O(V + E) because of the DFS in hasPath.
        """
        course = self.getCourse(courseCode).getCourseCode()
        prerequisite = self.getCourse(prerequisiteCode).getCourseCode()

        if course == prerequisite:
            raise ValueError("A course cannot be a prerequisite of itself.")
        if self._graph.hasEdge(prerequisite, course):
            raise ValueError(f"{prerequisite} is already a prerequisite of {course}.")
        if self._graph.hasPath(course, prerequisite):
            raise ValueError(f"Cannot add {prerequisite} as a prerequisite of {course}: "
                             f"{course} is already required (directly or indirectly) "
                             f"before {prerequisite}, so this would create a cycle.")

        self._graph.addEdge(prerequisite, course)

    def removePrerequisite(self, courseCode: str, prerequisiteCode: str) -> None:
        """Remove prerequisiteCode (Y) from courseCode (X): removes edge Y -> X."""
        course = self.getCourse(courseCode).getCourseCode()
        prerequisite = self.getCourse(prerequisiteCode).getCourseCode()

        if not self._graph.hasEdge(prerequisite, course):
            raise ValueError(f"{prerequisite} is not a direct prerequisite of {course}.")
        self._graph.removeEdge(prerequisite, course)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def getGraphAsText(self) -> str:
        """Adjacency-list view of the graph (prerequisite -> unlocked courses)."""
        return str(self._graph)

    @staticmethod
    def _normaliseCode(code) -> str:
        """Make user input consistent: ' cs201 ' -> 'CS201'."""
        if not isinstance(code, str):
            raise ValueError("Course code must be text.")
        return code.strip().upper()