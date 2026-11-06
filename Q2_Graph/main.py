"""
main.py

Menu-driven command-line interface for the Course Prerequisite System.

This file only handles INPUT and OUTPUT. All rules (validation, cycle checks,
course limit) live in CoursePrerequisiteSystem and Course, so the menu can
never put the data into an invalid state.

Run:  python main.py
"""

from course import Course, CourseType
from course_system import CoursePrerequisiteSystem
from seed_data import createSampleSystem

TITLE = "University Course Prerequisite System"
EXIT_CHOICE = "0"


# ======================================================================
# Input helpers (keep asking until the input is valid)
# ======================================================================
def promptText(message: str) -> str:
    """Ask until a non-empty answer is given."""
    while True:
        value = input(message).strip()
        if value:
            return value
        print("  Input cannot be empty. Please try again.")


def promptInt(message: str, minimum: int, maximum: int) -> int:
    """Ask until a whole number between minimum and maximum is given."""
    while True:
        value = input(message).strip()
        try:
            number = int(value)
        except ValueError:
            number = None
        if number is not None and minimum <= number <= maximum:
            return number
        print(f"  Please enter a whole number between {minimum} and {maximum}.")


def promptCourseType() -> CourseType:
    """Ask until C (Core) or E (Elective) is given."""
    choices = {"C": CourseType.CORE, "E": CourseType.ELECTIVE}
    while True:
        value = input("Enter Course Type (C = Core, E = Elective): ").strip().upper()
        if value in choices:
            return choices[value]
        print("  Please enter C or E.")


def promptExistingCourse(system: CoursePrerequisiteSystem, message: str) -> Course:
    """Ask for a course code and return the Course (ValueError if it does not exist)."""
    return system.getCourse(promptText(message))


# ======================================================================
# Output helper
# ======================================================================
def printCourseList(header: str, courses: list, emptyMessage: str) -> None:
    """Print a header followed by one course per line, or emptyMessage if none."""
    if not courses:
        print(emptyMessage)
        return
    print(header)
    for course in courses:
        print(f"  - {course.getCourseCode()} ({course.getCourseName()})")


# ======================================================================
# Mandatory features
# ======================================================================
def viewAllCourses(system: CoursePrerequisiteSystem) -> None:
    """Mandatory a: display a list of all courses' names."""
    courses = system.getAllCourses()
    print(f"\nAvailable Courses ({len(courses)}):")
    for number, course in enumerate(courses, start=1):
        print(f"{number}. {course}")


def viewCourseDetails(system: CoursePrerequisiteSystem) -> None:
    """Mandatory b: show ALL details of one course, ignoring core/elective."""
    course = promptExistingCourse(system, "Enter Course Code: ")
    print("\nCourse Details:")
    print(course.getFullDetails())


def viewPrerequisites(system: CoursePrerequisiteSystem) -> None:
    """Mandatory c: list the prerequisites (incoming edges) of a course."""
    course = promptExistingCourse(system, "Enter Course Code: ")
    printCourseList(f"\nPrerequisites for {course}:",
                    system.getPrerequisites(course.getCourseCode()),
                    f"\n{course} has no prerequisites.")


def viewUnlockedCourses(system: CoursePrerequisiteSystem) -> None:
    """Mandatory d: list the courses unlocked by a course (outgoing edges)."""
    course = promptExistingCourse(system, "Enter Course Code: ")
    printCourseList(f"\nCourses unlocked by {course}:",
                    system.getUnlockedCourses(course.getCourseCode()),
                    f"\n{course} does not unlock any course.")


# ======================================================================
# Optional (advanced) features
# ======================================================================
def viewCourseProfile(system: CoursePrerequisiteSystem) -> None:
    """Optional b: core shows all details, elective shows the name only."""
    course = promptExistingCourse(system, "Enter Course Code: ")
    print("\nCourse Profile:")
    print(course.getProfile())


def addNewCourse(system: CoursePrerequisiteSystem) -> None:
    """Optional a: create a new course (new vertex) on demand."""
    if system.getCourseCount() >= system.getMaxCourses():
        print(f"\nCannot add a course: the maximum of {system.getMaxCourses()} "
              f"courses has been reached.")
        return

    # Check the code first, so the user is not asked for details that will be rejected.
    code = Course.validateCode(promptText("Enter new Course Code: "))
    if system.hasCourse(code):
        raise ValueError(f"Course code '{code}' already exists.")

    name = promptText("Enter Course Name: ")
    creditHours = promptInt(f"Enter Credit Hours ({Course.MIN_CREDIT_HOURS}-"
                            f"{Course.MAX_CREDIT_HOURS}): ",
                            Course.MIN_CREDIT_HOURS, Course.MAX_CREDIT_HOURS)
    courseType = promptCourseType()
    description = input("Enter Description (optional): ")

    course = Course(code, name, creditHours, courseType, description)
    system.addCourse(course)
    print(f"\nCourse '{course}' added successfully. "
          f"({system.getCourseCount()}/{system.getMaxCourses()} courses)")


def addPrerequisiteToCourse(system: CoursePrerequisiteSystem) -> None:
    """Optional c: course X adds course Y as a prerequisite (new edge Y -> X)."""
    course = promptExistingCourse(system, "Enter Course Code (course X): ")
    prerequisite = promptExistingCourse(system, "Enter Prerequisite Course Code (course Y): ")

    system.addPrerequisite(course.getCourseCode(), prerequisite.getCourseCode())
    print(f"\n{prerequisite.getCourseCode()} is now a prerequisite of "
          f"{course.getCourseCode()}.")
    printCourseList(f"Updated prerequisites for {course}:",
                    system.getPrerequisites(course.getCourseCode()), "")


def removePrerequisiteFromCourse(system: CoursePrerequisiteSystem) -> None:
    """Optional d: course X removes course Y as a prerequisite (remove edge Y -> X)."""
    course = promptExistingCourse(system, "Enter Course Code (course X): ")
    current = system.getPrerequisites(course.getCourseCode())
    if not current:
        print(f"\n{course} has no prerequisites to remove.")
        return

    printCourseList(f"\nCurrent prerequisites for {course}:", current, "")
    prerequisite = promptExistingCourse(system, "Enter Prerequisite Course Code to remove (course Y): ")

    system.removePrerequisite(course.getCourseCode(), prerequisite.getCourseCode())
    print(f"\n{prerequisite.getCourseCode()} has been removed as a prerequisite of "
          f"{course.getCourseCode()}.")
    printCourseList(f"Updated prerequisites for {course}:",
                    system.getPrerequisites(course.getCourseCode()),
                    f"{course} now has no prerequisites.")


# ======================================================================
# Menu
# ======================================================================
# choice -> (label, handler function). Adding a feature = adding one line here.
MENU_OPTIONS = {
    "1": ("View All Courses", viewAllCourses),
    "2": ("View Course Details (All Information)", viewCourseDetails),
    "3": ("View Prerequisites of a Course", viewPrerequisites),
    "4": ("View Courses Unlocked by a Course", viewUnlockedCourses),
    "5": ("View Course Profile (Core/Elective Visibility)", viewCourseProfile),
    "6": ("Add a New Course", addNewCourse),
    "7": ("Add a Prerequisite to a Course", addPrerequisiteToCourse),
    "8": ("Remove a Prerequisite from a Course", removePrerequisiteFromCourse),
}


def displayMenu() -> None:
    print(f"\n==== {TITLE} ====")
    for choice, (label, _) in MENU_OPTIONS.items():
        print(f"{choice}. {label}")
    print(f"{EXIT_CHOICE}. Exit")


def run(system: CoursePrerequisiteSystem) -> None:
    """Main loop: show menu -> read choice -> run the matching feature."""
    while True:
        displayMenu()
        choice = input("Enter choice: ").strip()

        if choice == EXIT_CHOICE:
            print("Exiting program. Goodbye!")
            break
        if choice not in MENU_OPTIONS:
            print(f"Invalid choice '{choice}'. Please enter a number from the menu.")
            continue

        _, handler = MENU_OPTIONS[choice]
        try:
            handler(system)
        except ValueError as error:
            # Every rule violation is reported here; the program keeps running.
            print(f"\nError: {error}")


def main() -> None:
    system = createSampleSystem()
    try:
        run(system)
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C or end of input: exit cleanly instead of showing a traceback.
        print("\nProgram interrupted. Goodbye!")


if __name__ == "__main__":
    main()