"""
Unit tests for CoursePrerequisiteSystem and the sample (seed) data.

Run from the Q2_CourseGraph folder:
    python -m unittest -v
"""

import unittest

from course import Course, CourseType
from course_system import CoursePrerequisiteSystem
from seed_data import create_sample_system, COURSES, PREREQUISITES


def make_course(code, course_type=CourseType.CORE):
    return Course(code, f"Course {code}", 3, course_type)


def codes_of(courses):
    return [course.get_course_code() for course in courses]


class TestCourseOperations(unittest.TestCase):

    def setUp(self):
        self.system = CoursePrerequisiteSystem()
        self.system.add_course(make_course("CS101"))

    def test_add_and_get_course(self):
        self.assertTrue(self.system.has_course("CS101"))
        self.assertEqual(self.system.get_course("CS101").get_course_code(), "CS101")

    def test_lookup_is_case_insensitive(self):
        self.assertEqual(self.system.get_course("  cs101 ").get_course_code(), "CS101")

    def test_duplicate_code_rejected(self):
        with self.assertRaises(ValueError):
            self.system.add_course(make_course("cs101"))
        self.assertEqual(self.system.get_course_count(), 1)

    def test_non_course_rejected(self):
        with self.assertRaises(ValueError):
            self.system.add_course("CS999")

    def test_unknown_course_rejected(self):
        with self.assertRaises(ValueError):
            self.system.get_course("XX999")

    def test_maximum_course_limit(self):
        system = CoursePrerequisiteSystem(max_courses=2)
        system.add_course(make_course("A1"))
        system.add_course(make_course("A2"))
        with self.assertRaises(ValueError):
            system.add_course(make_course("A3"))
        self.assertEqual(system.get_course_count(), 2)

    def test_new_course_has_no_links(self):
        self.assertEqual(self.system.get_prerequisites("CS101"), [])
        self.assertEqual(self.system.get_unlocked_courses("CS101"), [])


class TestPrerequisites(unittest.TestCase):

    def setUp(self):
        # A -> B -> C   (A is a prerequisite of B, B of C);  D has no links
        self.system = CoursePrerequisiteSystem()
        for code in ("A1", "B1", "C1", "D1"):
            self.system.add_course(make_course(code))
        self.system.add_prerequisite("B1", "A1")
        self.system.add_prerequisite("C1", "B1")

    def test_prerequisites_and_unlocked_courses(self):
        self.assertEqual(codes_of(self.system.get_prerequisites("B1")), ["A1"])
        self.assertEqual(codes_of(self.system.get_unlocked_courses("B1")), ["C1"])

    def test_results_are_course_objects(self):
        for course in self.system.get_prerequisites("B1"):
            self.assertIsInstance(course, Course)

    def test_add_prerequisite(self):
        self.system.add_prerequisite("D1", "a1")          # case-insensitive input
        self.assertEqual(codes_of(self.system.get_prerequisites("D1")), ["A1"])
        self.assertEqual(codes_of(self.system.get_unlocked_courses("A1")), ["B1", "D1"])

    def test_self_prerequisite_rejected(self):
        with self.assertRaises(ValueError):
            self.system.add_prerequisite("A1", "A1")

    def test_duplicate_prerequisite_rejected(self):
        with self.assertRaises(ValueError):
            self.system.add_prerequisite("B1", "A1")

    def test_direct_cycle_rejected(self):
        # B1 already needs A1, so A1 cannot need B1.
        with self.assertRaises(ValueError):
            self.system.add_prerequisite("A1", "B1")

    def test_indirect_cycle_rejected(self):
        # A1 -> B1 -> C1 already exists, so A1 cannot need C1.
        with self.assertRaises(ValueError):
            self.system.add_prerequisite("A1", "C1")
        self.assertEqual(self.system.get_prerequisites("A1"), [])   # graph unchanged

    def test_unknown_course_in_prerequisite_rejected(self):
        with self.assertRaises(ValueError):
            self.system.add_prerequisite("A1", "ZZ999")
        with self.assertRaises(ValueError):
            self.system.add_prerequisite("ZZ999", "A1")

    def test_remove_prerequisite(self):
        self.system.remove_prerequisite("C1", "B1")
        self.assertEqual(self.system.get_prerequisites("C1"), [])
        self.assertEqual(self.system.get_unlocked_courses("B1"), [])

    def test_remove_missing_prerequisite_rejected(self):
        with self.assertRaises(ValueError):
            self.system.remove_prerequisite("C1", "A1")       # only indirect, not direct

    def test_cycle_allowed_again_after_removal(self):
        # After removing B1 -> C1, C1 is no longer after A1, so A1 may need C1.
        self.system.remove_prerequisite("C1", "B1")
        self.system.add_prerequisite("A1", "C1")
        self.assertEqual(codes_of(self.system.get_prerequisites("A1")), ["C1"])


class TestSeedData(unittest.TestCase):

    def setUp(self):
        self.system = create_sample_system()

    def test_course_count_within_brief_limits(self):
        self.assertTrue(5 <= self.system.get_course_count() <= 10)
        self.assertEqual(self.system.get_course_count(), len(COURSES))

    def test_all_prerequisite_links_loaded(self):
        for prerequisite, course in PREREQUISITES:
            self.assertIn(prerequisite, codes_of(self.system.get_prerequisites(course)))

    def test_has_both_core_and_elective(self):
        types = {course.get_course_type() for course in self.system.get_all_courses()}
        self.assertEqual(types, {CourseType.CORE, CourseType.ELECTIVE})

    def test_sample_scenarios(self):
        self.assertEqual(self.system.get_prerequisites("CS101"), [])                    # no prerequisites
        self.assertEqual(codes_of(self.system.get_prerequisites("CS201")), ["CS101", "MA101"])  # several
        self.assertEqual(codes_of(self.system.get_unlocked_courses("CS201")), ["CS202", "CS301"])
        self.assertEqual(self.system.get_unlocked_courses("CS302"), [])                  # unlocks none


if __name__ == "__main__":
    unittest.main()