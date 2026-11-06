"""
seed_data.py

Pre-defined test data: 8 courses and their prerequisite links.
Keeping the data here (not inside the menu code) avoids hardcoding and makes
the data easy to change.

Prerequisite graph as an adjacency list (arrow = "is a prerequisite of"):

    CS101 -> CS102, CS201
    MA101 -> CS201, CS301
    CS102 -> CS303
    CS201 -> CS202, CS301
    CS301 -> CS302
    CS202, CS302, CS303 -> (unlock nothing)
"""

from course import Course, CourseType
from course_system import CoursePrerequisiteSystem

# (code, name, credit hours, type, description)
COURSES = [
    ("CS101", "Introduction to Programming", 4, CourseType.CORE,
     "Programming fundamentals in Python: variables, control flow and functions."),
    ("MA101", "Discrete Mathematics", 3, CourseType.CORE,
     "Logic, sets, relations, combinatorics and graph theory basics."),
    ("CS102", "Object-Oriented Programming", 4, CourseType.CORE,
     "Classes, objects, encapsulation, inheritance and polymorphism."),
    ("CS201", "Data Structures", 4, CourseType.CORE,
     "Lists, stacks, queues, trees, hash tables and graphs."),
    ("CS202", "Database Systems", 3, CourseType.CORE,
     "Relational modelling, SQL and normalisation."),
    ("CS301", "Algorithms", 4, CourseType.CORE,
     "Algorithm design, complexity analysis, sorting and graph algorithms."),
    ("CS302", "Artificial Intelligence", 3, CourseType.ELECTIVE,
     "Search, knowledge representation and introductory machine learning."),
    ("CS303", "Web Development", 3, CourseType.ELECTIVE,
     "Front-end and back-end development of web applications."),
]

# (prerequisite, course): the first course must be completed before the second
PREREQUISITES = [
    ("CS101", "CS102"),
    ("CS101", "CS201"),
    ("MA101", "CS201"),
    ("CS201", "CS202"),
    ("CS201", "CS301"),
    ("MA101", "CS301"),
    ("CS301", "CS302"),
    ("CS102", "CS303"),
]


def createSampleSystem() -> CoursePrerequisiteSystem:
    """Build a system loaded with the sample courses and prerequisites.

    The data goes through the normal addCourse / addPrerequisite methods,
    so it is validated by the same rules (no duplicates, no cycles).
    """
    system = CoursePrerequisiteSystem()
    for code, name, credits, courseType, description in COURSES:
        system.addCourse(Course(code, name, credits, courseType, description))
    for prerequisite, course in PREREQUISITES:
        system.addPrerequisite(course, prerequisite)
    return system