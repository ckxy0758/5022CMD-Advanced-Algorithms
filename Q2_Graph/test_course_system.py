"""
Unit tests for CoursePrerequisiteSystem and the sample (seed) data.

Run from the Q2_CourseGraph folder:
    python -m unittest -v
"""

import unittest

from course import Course, CourseType
from course_system import CoursePrerequisiteSystem
from seed_data import createSampleSystem, COURSES, PREREQUISITES


def makeCourse(code, courseType=CourseType.CORE):
    return Course(code, f"Course {code}", 3, courseType)


def codesOf(courses):
    return [course.getCourseCode() for course in courses]


class TestCourseOperations(unittest.TestCase):

    def setUp(self):
        self.system = CoursePrerequisiteSystem()
        self.system.addCourse(makeCourse("CS101"))

    def test_add_and_get_course(self):
        self.assertTrue(self.system.hasCourse("CS101"))
        self.assertEqual(self.system.getCourse("CS101").getCourseCode(), "CS101")

    def test_lookup_is_case_insensitive(self):
        self.assertEqual(self.system.getCourse("  cs101 ").getCourseCode(), "CS101")

    def test_duplicate_code_rejected(self):
        with self.assertRaises(ValueError):
            self.system.addCourse(makeCourse("cs101"))
        self.assertEqual(self.system.getCourseCount(), 1)

    def test_non_course_rejected(self):
        with self.assertRaises(ValueError):
            self.system.addCourse("CS999")

    def test_unknown_course_rejected(self):
        with self.assertRaises(ValueError):
            self.system.getCourse("XX999")

    def test_maximum_course_limit(self):
        system = CoursePrerequisiteSystem(maxCourses=2)
        system.addCourse(makeCourse("A1"))
        system.addCourse(makeCourse("A2"))
        with self.assertRaises(ValueError):
            system.addCourse(makeCourse("A3"))
        self.assertEqual(system.getCourseCount(), 2)

    def test_new_course_has_no_links(self):
        self.assertEqual(self.system.getPrerequisites("CS101"), [])
        self.assertEqual(self.system.getUnlockedCourses("CS101"), [])


class TestPrerequisites(unittest.TestCase):

    def setUp(self):
        # A -> B -> C   (A is a prerequisite of B, B of C);  D has no links
        self.system = CoursePrerequisiteSystem()
        for code in ("A1", "B1", "C1", "D1"):
            self.system.addCourse(makeCourse(code))
        self.system.addPrerequisite("B1", "A1")
        self.system.addPrerequisite("C1", "B1")

    def test_prerequisites_and_unlocked_courses(self):
        self.assertEqual(codesOf(self.system.getPrerequisites("B1")), ["A1"])
        self.assertEqual(codesOf(self.system.getUnlockedCourses("B1")), ["C1"])

    def test_results_are_course_objects(self):
        for course in self.system.getPrerequisites("B1"):
            self.assertIsInstance(course, Course)

    def test_add_prerequisite(self):
        self.system.addPrerequisite("D1", "a1")          # case-insensitive input
        self.assertEqual(codesOf(self.system.getPrerequisites("D1")), ["A1"])
        self.assertEqual(codesOf(self.system.getUnlockedCourses("A1")), ["B1", "D1"])

    def test_self_prerequisite_rejected(self):
        with self.assertRaises(ValueError):
            self.system.addPrerequisite("A1", "A1")

    def test_duplicate_prerequisite_rejected(self):
        with self.assertRaises(ValueError):
            self.system.addPrerequisite("B1", "A1")

    def test_direct_cycle_rejected(self):
        # B1 already needs A1, so A1 cannot need B1.
        with self.assertRaises(ValueError):
            self.system.addPrerequisite("A1", "B1")

    def test_indirect_cycle_rejected(self):
        # A1 -> B1 -> C1 already exists, so A1 cannot need C1.
        with self.assertRaises(ValueError):
            self.system.addPrerequisite("A1", "C1")
        self.assertEqual(self.system.getPrerequisites("A1"), [])   # graph unchanged

    def test_unknown_course_in_prerequisite_rejected(self):
        with self.assertRaises(ValueError):
            self.system.addPrerequisite("A1", "ZZ999")
        with self.assertRaises(ValueError):
            self.system.addPrerequisite("ZZ999", "A1")

    def test_remove_prerequisite(self):
        self.system.removePrerequisite("C1", "B1")
        self.assertEqual(self.system.getPrerequisites("C1"), [])
        self.assertEqual(self.system.getUnlockedCourses("B1"), [])

    def test_remove_missing_prerequisite_rejected(self):
        with self.assertRaises(ValueError):
            self.system.removePrerequisite("C1", "A1")       # only indirect, not direct

    def test_cycle_allowed_again_after_removal(self):
        # After removing B1 -> C1, C1 is no longer after A1, so A1 may need C1.
        self.system.removePrerequisite("C1", "B1")
        self.system.addPrerequisite("A1", "C1")
        self.assertEqual(codesOf(self.system.getPrerequisites("A1")), ["C1"])


class TestSeedData(unittest.TestCase):

    def setUp(self):
        self.system = createSampleSystem()

    def test_course_count_within_brief_limits(self):
        self.assertTrue(5 <= self.system.getCourseCount() <= 10)
        self.assertEqual(self.system.getCourseCount(), len(COURSES))

    def test_all_prerequisite_links_loaded(self):
        for prerequisite, course in PREREQUISITES:
            self.assertIn(prerequisite, codesOf(self.system.getPrerequisites(course)))

    def test_has_both_core_and_elective(self):
        types = {course.getCourseType() for course in self.system.getAllCourses()}
        self.assertEqual(types, {CourseType.CORE, CourseType.ELECTIVE})

    def test_sample_scenarios(self):
        self.assertEqual(self.system.getPrerequisites("CS101"), [])                    # no prerequisites
        self.assertEqual(codesOf(self.system.getPrerequisites("CS201")), ["CS101", "MA101"])  # several
        self.assertEqual(codesOf(self.system.getUnlockedCourses("CS201")), ["CS202", "CS301"])
        self.assertEqual(self.system.getUnlockedCourses("CS302"), [])                  # unlocks none


if __name__ == "__main__":
    unittest.main()