"""
Unit tests for the Course entity class.

Run from the Q2_CourseGraph folder:
    python -m unittest -v
"""

import unittest

from course import Course, CourseType


class TestCourseCreation(unittest.TestCase):

    def test_valid_course_and_getters(self):
        course = Course("CS201", "Data Structures", 4, CourseType.CORE, "Lists and trees")
        self.assertEqual(course.getCourseCode(), "CS201")
        self.assertEqual(course.getCourseName(), "Data Structures")
        self.assertEqual(course.getCreditHours(), 4)
        self.assertEqual(course.getCourseType(), CourseType.CORE)
        self.assertEqual(course.getDescription(), "Lists and trees")
        self.assertTrue(course.isCore())

    def test_code_is_normalised(self):
        course = Course("  cs201 ", "Data Structures", 4, CourseType.CORE)
        self.assertEqual(course.getCourseCode(), "CS201")

    def test_str_format(self):
        course = Course("CS201", "Data Structures", 4, CourseType.CORE)
        self.assertEqual(str(course), "CS201 - Data Structures")


class TestCourseValidation(unittest.TestCase):

    def test_invalid_code(self):
        for badCode in ("", "   ", "CS 201", "CS-201", 201):
            with self.subTest(code=badCode), self.assertRaises(ValueError):
                Course(badCode, "Name", 3, CourseType.CORE)

    def test_empty_name(self):
        with self.assertRaises(ValueError):
            Course("CS201", "   ", 3, CourseType.CORE)

    def test_invalid_credit_hours(self):
        for badHours in (0, 7, -1, 3.5, "3", True):
            with self.subTest(hours=badHours), self.assertRaises(ValueError):
                Course("CS201", "Name", badHours, CourseType.CORE)

    def test_credit_hours_boundaries_are_valid(self):
        Course("CS201", "Name", Course.MIN_CREDIT_HOURS, CourseType.CORE)
        Course("CS202", "Name", Course.MAX_CREDIT_HOURS, CourseType.CORE)

    def test_invalid_course_type(self):
        with self.assertRaises(ValueError):
            Course("CS201", "Name", 3, "Core")      # must be the Enum, not a string


class TestCourseDisplay(unittest.TestCase):

    def setUp(self):
        self.core = Course("CS201", "Data Structures", 4, CourseType.CORE, "Lists and trees")
        self.elective = Course("CS305", "Computer Graphics", 3, CourseType.ELECTIVE, "2D/3D")

    def test_full_details_show_everything_for_elective(self):
        details = self.elective.getFullDetails()
        for text in ("CS305", "Computer Graphics", "3", "Elective", "2D/3D"):
            self.assertIn(text, details)

    def test_profile_of_core_shows_all_details(self):
        self.assertEqual(self.core.getProfile(), self.core.getFullDetails())

    def test_profile_of_elective_hides_details(self):
        profile = self.elective.getProfile()
        self.assertIn("Computer Graphics", profile)
        self.assertNotIn("CS305", profile)
        self.assertNotIn("2D/3D", profile)


if __name__ == "__main__":
    unittest.main()