import os
import time
import requests
from bs4 import BeautifulSoup
import threading
from threading import Event
from plyer import notification

application_name: str = "EIS Grade Notifier"
student_name: str = ""
student_honorific: str = ""
website_url: str = "https://eis.epoka.edu.al/login"
student_page_url: str = "https://eis.epoka.edu.al/student/"
grade_url: str = "https://eis.epoka.edu.al/student/interimGrades"
remember: bool = False
mobile_notification: bool = False
desktop_notification: bool = True
logged_in: bool = False
session: requests.Session = requests.Session()
_course_data: list = []
want_to_exit: bool = False
logged_out: bool = True
exit_event = Event()
update_timeout: int = 300  # 5 minutes timeout to refresh the grades


# Display about
def display_about():
    clear()
    print("About")
    print("""
    This application was created by:
    - Detjon Mataj
    
    The main reason for creating this application is to help students keep track of their grades.
    After finishing the exams, students wait impatiently for the results to be published.
    They will be notified in real time, so they can check their grades as soon as they are available.
    Don't worry no needed to refresh the page anymore :).
    
    This application is not intended to be used by anyone other than the students of the Epoka University Students.
    """)

    input("\nPress enter to return to the main menu.")
    display_main_menu()


# Display Main Menu
def display_main_menu():
    global want_to_exit
    clear()
    print("Main Menu\n")
    print("1. Login")
    print("2. Help")
    print("3. About")
    print("0. Exit")
    while True:
        choice = input("Enter your choice: ")
        if choice == "1":
            clear()
            login()
            break
        elif choice == "2":
            display_help()
            break
        elif choice == "3":
            display_about()
            break
        elif choice == "0":
            print("Goodbye")
            want_to_exit = True
            exit_event.set()
            break
        else:
            print("Invalid choice")
            continue
    return


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def get_response(url: str):
    global session
    if not session:
        session = requests.Session()
    return session.get(url)


def validate_session(status_code, soup):
    if status_code == 200 and soup.find('h3', {'class': 'page-title'}):
        return True
    else:
        return False


def get_course_data():
    courses_data: list = []
    response = get_response(grade_url)
    soup = BeautifulSoup(response.text, "html.parser")
    # Get all courses and their grades
    courses_soup = soup.find_all('div', {'class': 'row'})[2]
    for i, course_soup in enumerate(courses_soup.find_all('div', {'class': 'portlet box purple'})):
        course_name = course_soup.find('div', {'class': 'caption'}).text.strip()
        table_headers = course_soup.find('table', {'class': 'table table-striped table-hover interim-grades-table'}) \
            .find('thead').find_all('th')
        table_rows = course_soup.find('table', {'class': 'table table-striped table-hover interim-grades-table'}) \
            .find('tbody').find_all('tr')
        assignments: list = []
        for row in table_rows:
            assigment: dict = {}
            for j, table_header in enumerate(table_headers):
                assigment[table_header.text.strip().replace("\n", "")] = row.find_all('td')[j].text.strip() \
                    .replace("\n", "").replace(" %", "%")
            assignments.append(assigment)
        course_notes = list(
            map(lambda x: x.strip(), course_soup.find('div', {'class': 'note'}).find('p')
                .text.strip().replace("\n", "").split("|")))

        course_notes = list(map(lambda x: x.split(":"), course_notes))
        course_notes = dict(map(lambda x: (x[0].strip().replace("\n", ""), x[1].strip().replace("\n", "")),
                                course_notes))
        course_completed = course_soup.find('input', {'class': 'knob'})['value'] + "%"
        course_notes['Completed'] = course_completed

        courses_data.append(
            {
                "course_name": course_name,
                "assignments": assignments,
                "course_notes": course_notes,
            }
        )

    return courses_data


def display_course_data(course_data):
    print(f"Course: {course_data['course_name']}")

    # Max key size
    max_key_size = max(map(lambda z: len(z), course_data['assignments'][0].keys())) + 1
    total_size = max_key_size + len(course_data['assignments'][0]["Date/Time"]) + 2

    print("\n\tCourse Assignments:")
    # print all assignments
    print("\t" + "-" * total_size)
    for x, assignment in enumerate(course_data['assignments']):
        for key, value in assignment.items():
            print(f"\t{key:<{max_key_size}}: {value}")
        print("\t" + "-" * total_size)

    print("\n\n\tOverall course results:")
    max_key_size += 1
    print("\t" + "-" * total_size)
    for key, value in course_data['course_notes'].items():
        print(f"\t{key:<{max_key_size}}: {value}")
    print("\t" + "-" * total_size)


def view_grades():
    print("View Grades")
    course_data: list = get_course_data()
    print("For which course do you want to view grades?")
    for i, course in enumerate(course_data):
        print(f"{i + 1}. {course['course_name']}")
    print("9. All courses")
    print("10. Refresh")
    print("0. Go back")
    while True:
        course_choice = input("Enter your choice: ")
        if course_choice == "0":
            dashboard()
            break
        elif course_choice.isdigit() and int(course_choice) <= len(course_data):
            clear()
            display_course_data(course_data[int(course_choice) - 1])
            while True:
                print("1. Refresh")
                print("2. Back")
                print("0. Return to Dashboard")
                choice = input("Enter your choice: ")
                if choice == "1":
                    clear()
                    course_data = get_course_data()
                    display_course_data(course_data[int(course_choice) - 1])
                    continue
                if choice == "2":
                    clear()
                    view_grades()
                    break
                elif choice == "0":
                    clear()
                    dashboard()
                    break
                else:
                    print("Invalid choice")
                    continue
            break
        elif course_choice == "9":
            clear()
            for course in course_data:
                display_course_data(course)
                print("\n")
            while True:
                print("1. Refresh")
                print("2. Back")
                print("0. Return to Dashboard")
                choice = input("Enter your choice: ")
                if choice == "1":
                    clear()
                    course_data = get_course_data()
                    for course in course_data:
                        display_course_data(course)
                    continue
                if choice == "2":
                    clear()
                    view_grades()
                    break
                elif choice == "0":
                    clear()
                    dashboard()
                    break
                else:
                    print("Invalid choice")
                    continue
            break
        elif course_choice == "10":
            clear()
            view_grades()
            continue
        else:
            print("Invalid choice")
            continue


def logout():
    global logged_in, session, logged_out, _course_data
    logged_in = False
    logged_out = True
    _course_data = []
    if session:
        session.close()
    print("Logout")
    clear()
    display_main_menu()


def refresh():
    update_course_data()


def dashboard_menu():
    global desktop_notification
    global mobile_notification
    global session
    print(f"Dashboard Menu")
    print(f"1. View Grades")
    print(f"2. Logout")
    print(f"3. Desktop Notification {'(ON)' if desktop_notification else '(OFF)'}")
    print(f"4. Mobile Notification{'(ON)' if mobile_notification else '(OFF)'}")
    print(f"5. Refresh")
    while True:
        choice = input("Enter your choice: ")
        if choice == "1":
            clear()
            view_grades()
            break
        elif choice == "2":
            clear()
            logout()
            break
        elif choice == "3":
            clear()
            desktop_notification = not desktop_notification
            dashboard_menu()
            break
        elif choice == "4":
            print("Not implemented")
            time.sleep(1)
            clear()
            # mobile_notification = not mobile_notification
            dashboard_menu()
            break
        elif choice == "5":
            refresh()
            clear()
            dashboard()
            break
        else:
            print("Invalid choice")
            continue


def dashboard():
    global session
    clear()
    print(f"Welcome {student_honorific}. {student_name}!")
    dashboard_menu()


def login():
    global logged_in, logged_out
    print("Login to your account")
    print("If you don't know where to get your cookie, please go back and check help section:")
    if input("Do you have a cookie? (y/n): ") == "y":
        cookie = input("Enter PHPSESSID cookie: ")
        status_code, soup = create_session(cookie)
        if validate_session(status_code, soup):
            clear()
            print("Login successful")
            logged_in = True
            logged_out = False
            time.sleep(1)
            background_thread = threading.Thread(target=background_tasks)
            background_thread.start()
            clear()
            dashboard()
        else:
            clear()
            print("Login failed\n")
            login()
    else:
        clear()
        display_main_menu()


def remember_me():
    pass


def create_session(cookie: str):
    global student_name
    global student_honorific
    global session
    if session:
        session.close()
    session = requests.Session()
    session.cookies.set("PHPSESSID", cookie, domain="eis.epoka.edu.al")
    response = get_response(grade_url)
    r = get_response(student_page_url)
    if r and r.status_code == 200:
        page_title = BeautifulSoup(r.text, "html.parser").find('h3', {'class': 'page-title'})
        if page_title:
            metadata = page_title.text.strip().replace("\n", "").replace("Welcome ", "")
            student_honorific = metadata.split(". ")[0].strip()
            student_name = metadata.split(". ")[1].strip()
    return response.status_code, BeautifulSoup(response.text, "html.parser")


# Display Help Menu
def display_help():
    print("Help Menu\n\n")
    print("""
    You first need to login to your EIS account.\n
    Then you need to get your PHPSESSID cookie.\n
    You can do this by using this chrome extension:\n
    https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg\n
    Once you have the cookie, you can login to your account using this application.\n
    """)

    input("\nPress enter to return to the main menu.")
    display_main_menu()


def user_interface():
    clear()
    print("Welcome to the EIS Grade Notifier")
    while not want_to_exit:
        display_main_menu()
    return


def get_changes(old_version: list, new_version: list):
    changes = []
    for i, old_version_course in enumerate(old_version):
        course_changes = {
            'course_name': old_version_course['course_name'],
            'assignment_changes': {}
        }
        if len(old_version_course["assignments"]) != len(new_version[i]["assignments"]):
            course_changes['new_assignments'] = [assignment for assignment in new_version[i]["assignments"]
                                                 if assignment["Name"] not in [a["Name"]
                                                                               for a in
                                                                               old_version_course["assignments"]]]
        # Check if any of the old assignments' data has changed
        for j, old_version_assignment in enumerate(old_version_course["assignments"]):
            # Check if the assigment grade has changed
            if old_version_assignment["Grade"] != new_version[i]["assignments"][j]["Grade"]:
                course_changes['assignment_changes'][old_version_assignment["Name"]] = {
                    'grades_changed': {
                        'old_grade': old_version_assignment['Grade'],
                        'new_grade': new_version[i]["assignments"][j]["Grade"]
                    },
                }
            else:
                # Check if the assigment class average has changed
                # It is considered a change if previous class average was - and now is not
                # The professor may publish grade of another student and the class average changes.
                # Why would you want to receive notification when the class average changes?
                # The reason why I'm checking if the class average was - and when it changes to a number
                # (at least one student received their grade) and you will probably receive your grade soon.
                # P.s '-' indicates that the class average is not available yet so no student received their grade
                if old_version_assignment["Class Average"] == '-' and \
                        new_version[i]["assignments"][j]["Class Average"] != '-':
                    course_changes['assignment_changes'][old_version_assignment["Name"]] = {
                        'class_average_changed': {
                            'old_class_average': old_version_assignment['Class Average'],
                            'new_class_average': new_version[i]["assignments"][j]["Class Average"]
                        },
                    }

        if len(course_changes.keys()) > 2 or len(course_changes['assignment_changes'].keys()) > 0:
            changes.append(course_changes)

    return changes


def send_notification(title: str, message: str):
    if desktop_notification:
        notification.notify(
            title=title,
            message=message,
            app_icon="icon.ico",
            timeout=5,
        )
        time.sleep(5)

    if mobile_notification:
        pass


def get_changes_message(changes: list) -> list:
    messages = []
    for change in changes:
        if 'new_assignments' in change:
            if len(change['new_assignments']) == 1:
                # The professor added a new assigment and published the grade
                # This means the grade is not -
                if change['new_assignments'][0]['Grade'] != '-':
                    messages.append(
                        {
                            'title': f"{change['course_name']} - New Assignment",
                            'message': f"Looks like the professor added a new assignment and published your grade "
                                       f"for assigment {change['new_assignments'][0]['Name']} "
                                       f"of the course {change['course_name']}."
                                       f"Yor grade is {change['new_assignments'][0]['Grade']}."
                        }
                    )
                elif change['new_assignments'][0]['Class Average'] != '-' \
                        and change['new_assignments'][0]['Grade'] == '-':
                    messages.append(
                        {
                            'title': f"{change['course_name']} - New Assignment",
                            'message': f"Looks like the professor added a new assignment and he may publish your grade "
                                       f"soon for assigment {change['new_assignments'][0]['Name']} "
                                       f"of the course {change['course_name']}."
                        }
                    )
                else:
                    messages.append(
                        {
                            'title': f"{change['course_name']} - New Assignment",
                            'message': f"Looks like the professor added a new assignment for assigment "
                                       f"{change['new_assignments'][0]['Name']} "
                                       f"of the course {change['course_name']}."
                        }
                    )

            elif len(change['new_assignments']) > 1:
                word = 'assignments' if len(change['new_assignments']) > 1 else 'assignment'
                # List of new assignments that the professor is publishing grades
                # The assigment Class Average is != - and the Grade is -
                assignments_publishing_grades = [a for a in change['new_assignments'] if
                                                 a['Class Average'] != '-' and a['Grade'] == '-']
                # Assignments with published grades
                assignments_with_grades = [a for a in change['new_assignments']
                                           if a['Grade'] != '-' and a['Class Average'] != '-']
                # Message to be sent to the user when there are new assignments but no grade was published yet
                if len(assignments_publishing_grades) == 0 and len(assignments_with_grades) == 0:
                    messages.append({
                        'title': f"New {word} in {change['course_name']}",
                        'message': f"Looks like your professor created a new {word} "
                                   f"for the course {change['course_name']}."
                    })
                elif len(assignments_publishing_grades) > 0:
                    # Message to be sent to the user when there are new assignments and the professor is publishing
                    # grades for the other students and didn't publish your grade/s yet
                    messages.append({
                        'title': f"New {word} in {change['course_name']}",
                        'message': f"Looks like your professor created a new {word} "
                                   f"for the course {change['course_name']}."
                                   f"He is publishing grades for the {word}: "
                                   f"{', '.join([a['Name'] for a in assignments_publishing_grades])}"[:-1] + '.'
                    })
                # elif len(assignments_with_grades) > 0:
                else:
                    # Message to be sent to the user when there are new assignments
                    # and the professor has published his grade/s
                    messages.append({
                        'title': f"New {word} in {change['course_name']}",
                        'message': f"Looks like your professor created a new {word} "
                                   f"for the course {change['course_name']} and published your grade/s."
                        # f"He published your grades for the {word}:\n"
                        # f"{', '.join([a['Name'] for a in assignments_with_grades])}"[:-1] + '.'
                    })
        if len(change['assignment_changes'].keys()) > 0:
            for assignment_name, changes in change['assignment_changes'].items():
                if 'grades_changed' in changes:
                    if changes['grades_changed']['old_grade'] == '-':
                        messages.append({
                            'title': f"Publishes in {change['course_name']} "
                                     f" course.",
                            'message': f"Looks like your professor published your grade for the assigment"
                                       f"{assignment_name} in {change['course_name']}."
                                       f"Your grade is {changes['grades_changed']['new_grade']}."
                        })
                    else:
                        messages.append({
                            'title': f"Updates in {change['course_name']} course",
                            'message': f"Looks like your professor changed your grade for the assigment "
                                       f"{assignment_name} in {change['course_name']}."
                                       f"Your grade was {changes['grades_changed']['old_grade']} "
                                       f"and updated grade is {changes['grades_changed']['new_grade']}."
                        })
                else:
                    if 'class_average_changed' in changes:
                        messages.append({
                            'title': f"Updates in {change['course_name']}",
                            'message': f"Looks like your professor may publish soon your grade for the assigment"
                                       f"{assignment_name} in {change['course_name']} course."
                        })

    return messages


def check_for_updates_event():
    global session, want_to_exit, exit_event, logged_in, logged_out
    while not want_to_exit and logged_in and not logged_out and session is not None:
        if exit_event.is_set():
            exit_event = Event()

        update_course_data()

        exit_event.wait(update_timeout)
    else:
        exit_event.set()
        if not logged_out and session is None:
            logout()
        return


def update_course_data():
    global _course_data
    if len(_course_data) == 0:
        _course_data = get_course_data()
    else:
        new_course_data = get_course_data()
        changes = get_changes(_course_data, new_course_data)
        if len(changes) > 0:
            messages = get_changes_message(changes)
            for message in messages:
                send_notification(message['title'], message['message'])
            _course_data = new_course_data


def background_tasks():
    threading.Thread(target=check_for_updates_event).start()
    return


def run():
    clear()
    user_interface_thread = threading.Thread(target=user_interface)
    user_interface_thread.start()


def main():
    run()


if __name__ == "__main__":
    main()
