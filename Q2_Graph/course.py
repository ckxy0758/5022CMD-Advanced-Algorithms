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
    getters only (no setters). In particular, course_code must never change,
    because it is used as the vertex key in the prerequisite graph.
    """

    MIN_CREDIT_HOURS = 1
    MAX_CREDIT_HOURS = 6

    def __init__(self, course_code: str, course_name: str, credit_hours: int,
                 course_type: CourseType, description: str = ""):
        self._course_code = self.validate_code(course_code)
        self._course_name = self._validate_name(course_name)
        self._credit_hours = self._validate_credit_hours(credit_hours)
        self._course_type = self._validate_course_type(course_type)
        self._description = description.strip() if isinstance(description, str) else ""

    # ------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------
    def get_course_code(self) -> str:
        return self._course_code

    def get_course_name(self) -> str:
        return self._course_name

    def get_credit_hours(self) -> int:
        return self._credit_hours

    def get_course_type(self) -> CourseType:
        return self._course_type

    def get_description(self) -> str:
        return self._description

    def is_core(self) -> bool:
        return self._course_type == CourseType.CORE

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------
    def get_full_details(self) -> str:
        """All information, ignoring visibility (Mandatory feature b)."""
        return (f"Course Code  : {self._course_code}\n"
                f"Course Name  : {self._course_name}\n"
                f"Credit Hours : {self._credit_hours}\n"
                f"Course Type  : {self._course_type.value}\n"
                f"Description  : {self._description or '-'}")

    def get_profile(self) -> str:
        """Visibility-aware profile (Optional feature b).

        Core courses show all details; elective courses show the name only.
        """
        if self.is_core():
            return self.get_full_details()
        return f"Course Name  : {self._course_name}"

    def __str__(self) -> str:
        """Short one-line form, e.g. 'CS201 - Data Structures'."""
        return f"{self._course_code} - {self._course_name}"

    # ------------------------------------------------------------------
    # Validation helpers (internal)
    # ------------------------------------------------------------------
    @staticmethod
    def validate_code(code) -> str:
        """Validate and normalise a course code. Public so the menu can check a
        new code BEFORE asking for the other details."""
        if not isinstance(code, str):
            raise ValueError("Course code must be text.")
        code = code.strip().upper()            # ' cs201 ' -> 'CS201'
        if not code or not code.isalnum():
            raise ValueError("Course code must contain letters/digits only, e.g. CS201.")
        return code

    @staticmethod
    def _validate_name(name) -> str:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Course name cannot be empty.")
        return name.strip()

    @classmethod
    def _validate_credit_hours(cls, hours) -> int:
        # bool is a subclass of int in Python (True == 1), so reject it explicitly.
        if isinstance(hours, bool) or not isinstance(hours, int):
            raise ValueError("Credit hours must be a whole number.")
        if not cls.MIN_CREDIT_HOURS <= hours <= cls.MAX_CREDIT_HOURS:
            raise ValueError(f"Credit hours must be between "
                             f"{cls.MIN_CREDIT_HOURS} and {cls.MAX_CREDIT_HOURS}.")
        return hours

    @staticmethod
    def _validate_course_type(course_type) -> CourseType:
        if not isinstance(course_type, CourseType):
            raise ValueError("Course type must be CourseType.CORE or CourseType.ELECTIVE.")
        return course_type