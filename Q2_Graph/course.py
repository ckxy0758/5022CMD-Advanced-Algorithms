"""
course.py

Domain / entity classes for the Course Prerequisite System.
This module knows nothing about graphs - it only describes a single course.
"""

from enum import Enum


class CourseType(Enum):
    """The two allowed course types. An Enum prevents typos such as 'core' vs 'Core'."""
    CORE = "Core"
    ELECTIVE = "Elective"


class Course:
    """Represents a single course offered by a university.

    The attributes are validated once in the constructor and exposed through
    getters only (no setters). In particular, courseCode must never change,
    because it is used as the vertex key in the prerequisite graph.
    """

    MIN_CREDIT_HOURS = 1
    MAX_CREDIT_HOURS = 6

    def __init__(self, courseCode: str, courseName: str, creditHours: int,
                 courseType: CourseType, description: str = ""):
        self._courseCode = self.validateCode(courseCode)
        self._courseName = self._validateName(courseName)
        self._creditHours = self._validateCreditHours(creditHours)
        self._courseType = self._validateCourseType(courseType)
        self._description = description.strip() if isinstance(description, str) else ""

    # ------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------
    def getCourseCode(self) -> str:
        return self._courseCode

    def getCourseName(self) -> str:
        return self._courseName

    def getCreditHours(self) -> int:
        return self._creditHours

    def getCourseType(self) -> CourseType:
        return self._courseType

    def getDescription(self) -> str:
        return self._description

    def isCore(self) -> bool:
        return self._courseType == CourseType.CORE

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------
    def getFullDetails(self) -> str:
        """All information, ignoring visibility (Mandatory feature b)."""
        return (f"Course Code  : {self._courseCode}\n"
                f"Course Name  : {self._courseName}\n"
                f"Credit Hours : {self._creditHours}\n"
                f"Course Type  : {self._courseType.value}\n"
                f"Description  : {self._description or '-'}")

    def getProfile(self) -> str:
        """Visibility-aware profile (Optional feature b).

        Core courses show all details; elective courses show the name only.
        """
        if self.isCore():
            return self.getFullDetails()
        return (f"Course Name  : {self._courseName}\n"
                f"(Elective course - other details are hidden)")

    def __str__(self) -> str:
        """Short one-line form, e.g. 'CS201 - Data Structures'."""
        return f"{self._courseCode} - {self._courseName}"

    # ------------------------------------------------------------------
    # Validation helpers (internal)
    # ------------------------------------------------------------------
    @staticmethod
    def validateCode(code) -> str:
        """Validate and normalise a course code. Public so the menu can check a
        new code BEFORE asking for the other details."""
        if not isinstance(code, str):
            raise ValueError("Course code must be text.")
        code = code.strip().upper()            # ' cs201 ' -> 'CS201'
        if not code or not code.isalnum():
            raise ValueError("Course code must contain letters/digits only, e.g. CS201.")
        return code

    @staticmethod
    def _validateName(name) -> str:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Course name cannot be empty.")
        return name.strip()

    @classmethod
    def _validateCreditHours(cls, hours) -> int:
        # bool is a subclass of int in Python (True == 1), so reject it explicitly.
        if isinstance(hours, bool) or not isinstance(hours, int):
            raise ValueError("Credit hours must be a whole number.")
        if not cls.MIN_CREDIT_HOURS <= hours <= cls.MAX_CREDIT_HOURS:
            raise ValueError(f"Credit hours must be between "
                             f"{cls.MIN_CREDIT_HOURS} and {cls.MAX_CREDIT_HOURS}.")
        return hours

    @staticmethod
    def _validateCourseType(courseType) -> CourseType:
        if not isinstance(courseType, CourseType):
            raise ValueError("Course type must be CourseType.CORE or CourseType.ELECTIVE.")
        return courseType