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
from seed_data import create_sample_system

TITLE = "University Course Prerequisite System"
EXIT_CHOICE = "0"


# ======================================================================
# Input helpers (keep asking until the input is valid)
# ======================================================================
def prompt_text(message: str) -> str:
    """Ask until a non-empty answer is given."""
    while True:
        value = input(message).strip()
        if value:
            return value
        print("  Input cannot be empty. Please try again.")


def prompt_int(message: str, minimum: int, maximum: int) -> int:
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


def prompt_course_type() -> CourseType:
    """Ask until C (Core) or E (Elective) is given."""
    choices = {"C": CourseType.CORE, "E": CourseType.ELECTIVE}
    while True:
        value = input("Enter Course Type (C = Core, E = Elective): ").strip().upper()
        if value in choices:
            return choices[value]
        print("  Please enter C or E.")


def prompt_existing_course(system: CoursePrerequisiteSystem, message: str) -> Course:
    """Ask for a course code and return the Course (ValueError if it does not exist)."""
    return system.get_course(prompt_text(message))


# ======================================================================
# Output helper
# ======================================================================
def print_course_list(header: str, courses: list, empty_message: str) -> None:
    """Print a header followed by one course per line, or empty_message if none."""
    if not courses:
        print(empty_message)
        return
    print(header)
    for course in courses:
        print(f"  - {course.get_course_code()} ({course.get_course_name()})")


# ======================================================================
# Mandatory features
# ======================================================================
def view_all_courses(system: CoursePrerequisiteSystem) -> None:
    """Mandatory a: display a list of all courses' names."""
    courses = system.get_all_courses()
    print(f"\nAvailable Courses ({len(courses)}):")
    for number, course in enumerate(courses, start=1):
        print(f"{number}. {course}")


def view_course_details(system: CoursePrerequisiteSystem) -> None:
    """Mandatory b: show ALL details of one course, ignoring core/elective."""
    course = prompt_existing_course(system, "Enter Course Code: ")
    print("\nCourse Details:")
    print(course.get_full_details())


def view_prerequisites(system: CoursePrerequisiteSystem) -> None:
    """Mandatory c: list the prerequisites (incoming edges) of a course."""
    course = prompt_existing_course(system, "Enter Course Code: ")
    print_course_list(f"\nPrerequisites for {course}:",
                    system.get_prerequisites(course.get_course_code()),
                    f"\n{course} has no prerequisites.")


def view_unlocked_courses(system: CoursePrerequisiteSystem) -> None:
    """Mandatory d: list the courses unlocked by a course (outgoing edges)."""
    course = prompt_existing_course(system, "Enter Course Code: ")
    print_course_list(f"\nCourses unlocked by {course}:",
                    system.get_unlocked_courses(course.get_course_code()),
                    f"\n{course} does not unlock any course.")


# ======================================================================
# Optional (advanced) features
# ======================================================================
def view_course_profile(system: CoursePrerequisiteSystem) -> None:
    """Optional b: core shows all details, elective shows the name only."""
    course = prompt_existing_course(system, "Enter Course Code: ")
    print("\nCourse Profile:")
    print(course.get_profile())


def add_new_course(system: CoursePrerequisiteSystem) -> None:
    """Optional a: create a new course (new vertex) on demand."""
    if system.get_course_count() >= system.get_max_courses():
        print(f"\nCannot add a course: the maximum of {system.get_max_courses()} "
              f"courses has been reached.")
        return

    # Check the code first, so the user is not asked for details that will be rejected.
    code = Course.validate_code(prompt_text("Enter new Course Code: "))
    if system.has_course(code):
        raise ValueError(f"Course code '{code}' already exists.")

    name = prompt_text("Enter Course Name: ")
    credit_hours = prompt_int(f"Enter Credit Hours ({Course.MIN_CREDIT_HOURS}-"
                            f"{Course.MAX_CREDIT_HOURS}): ",
                            Course.MIN_CREDIT_HOURS, Course.MAX_CREDIT_HOURS)
    course_type = prompt_course_type()
    description = input("Enter Description (optional): ")

    course = Course(code, name, credit_hours, course_type, description)
    system.add_course(course)
    print(f"\nCourse '{course}' added successfully. "
          f"({system.get_course_count()}/{system.get_max_courses()} courses)")


def add_prerequisite_to_course(system: CoursePrerequisiteSystem) -> None:
    """Optional c: course X adds course Y as a prerequisite (new edge Y -> X)."""
    course = prompt_existing_course(
        system, "Enter the code of Course X (the course that needs the prerequisite): ")
    prerequisite = prompt_existing_course(
        system, "Enter the code of Course Y (the prerequisite to be completed first): ")

    system.add_prerequisite(course.get_course_code(), prerequisite.get_course_code())
    print(f"\n{prerequisite.get_course_code()} is now a prerequisite of "
          f"{course.get_course_code()}.")
    print_course_list(f"Updated prerequisites for {course}:",
                    system.get_prerequisites(course.get_course_code()), "")


def remove_prerequisite_from_course(system: CoursePrerequisiteSystem) -> None:
    """Optional d: course X removes course Y as a prerequisite (remove edge Y -> X)."""
    course = prompt_existing_course(
        system, "Enter the code of Course X (the course whose prerequisite will be removed): ")
    current = system.get_prerequisites(course.get_course_code())
    if not current:
        print(f"\n{course} has no prerequisites to remove.")
        return

    print_course_list(f"\nCurrent prerequisites for {course}:", current, "")
    prerequisite = prompt_existing_course(
        system, "Enter the code of Course Y (the prerequisite to remove): ")

    system.remove_prerequisite(course.get_course_code(), prerequisite.get_course_code())
    print(f"\n{prerequisite.get_course_code()} has been removed as a prerequisite of "
          f"{course.get_course_code()}.")
    print_course_list(f"Updated prerequisites for {course}:",
                    system.get_prerequisites(course.get_course_code()),
                    f"{course} now has no prerequisites.")


# ======================================================================
# Menu
# ======================================================================
# choice -> (label, handler function). Adding a feature = adding one line here.
MENU_OPTIONS = {
    "1": ("View All Courses", view_all_courses),
    "2": ("View Course Details (All Information)", view_course_details),
    "3": ("View Prerequisites of a Course", view_prerequisites),
    "4": ("View Courses Unlocked by a Course", view_unlocked_courses),
    "5": ("View Course Profile (Core/Elective Visibility)", view_course_profile),
    "6": ("Add a New Course", add_new_course),
    "7": ("Add a Prerequisite to a Course", add_prerequisite_to_course),
    "8": ("Remove a Prerequisite from a Course", remove_prerequisite_from_course),
}


def display_menu() -> None:
    print(f"\n==== {TITLE} ====")
    for choice, (label, _) in MENU_OPTIONS.items():
        print(f"{choice}. {label}")
    print(f"{EXIT_CHOICE}. Exit")


def run(system: CoursePrerequisiteSystem) -> None:
    """Main loop: show menu -> read choice -> run the matching feature."""
    while True:
        display_menu()
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
    system = create_sample_system()
    try:
        run(system)
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C or end of input: exit cleanly instead of showing a traceback.
        print("\nProgram interrupted. Goodbye!")


if __name__ == "__main__":
    main()