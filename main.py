import os
import time
import requests
from bs4 import BeautifulSoup
import threading
from plyer import notification

application_name: str = "EIS Grade Notifier"
student_name: str = ""
student_honorific: str = ""
website_url: str = "https://eis.epoka.edu.al/login"
student_page_url: str = "https://eis.epoka.edu.al/student/"
grade_url: str = "https://eis.epoka.edu.al/student/interimGrades"
remember: bool = False
mobile_notification: bool = False
desktop_notification: bool = False
logged_in: bool = False
session = None
_course_data: list = []
want_to_exit: bool = False


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
            map(lambda x: x.strip(), course_soup.find('div', {'class': 'note note-info'}).find('p')
                .text.strip().replace("\n", "").split("|")))

        course_notes = list(map(lambda x: x.split(":"), course_notes))
        course_notes = dict(map(lambda x: (x[0].strip().replace("\n", ""), x[1].strip().replace("\n", "")),
                                course_notes))
        courses_data.append(
            {
                "course_name": course_name,
                "assignments": assignments,
                "course_notes": course_notes
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
    global logged_in
    logged_in = False
    print("Logout")
    clear()
    display_main_menu()


def refresh():
    pass


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
    global logged_in
    print("Login to your account")
    print("If you don't know where to get your cookie, please go back and check help section:")
    if input("Do you have a cookie? (y/n): ") == "y":
        cookie = input("Enter PHPSESSID cookie: ")
        status_code, soup = create_session(cookie)
        if validate_session(status_code, soup):
            clear()
            print("Login successful")
            logged_in = True
            time.sleep(1)
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
    for i, course in enumerate(old_version):
        course_changes = {
            'course_name': course['course_name'],
        }
        if len(course["assignments"]) != len(new_version[i]["assignments"]):
            course_changes['new_assignments'] = [assignment for assignment in new_version[i]["assignments"]
                                                 if assignment not in course["assignments"]]
        # Check if any of the assignments' data has changed
        for j, assignment in enumerate(course["assignments"]):
            # Check if the assigment grade has changed
            if assignment["Grade"] != new_version[i]["assignments"][j]["Grade"]:
                course_changes['grades_changed'] = {
                    'assignment_name': assignment['Name'],
                    'old_grade': assignment['grade'],
                    'new_grade': new_version[i]["assignments"][j]["Grade"],
                }
            # Check if the assigment class average has changed
            if assignment["Class Average"] != new_version[i]["assignments"][j]["Class Average"]:
                course_changes['class_average_changed'] = {
                    'assignment_name': assignment['Name'],
                    'old_class_average': assignment["Class Average"],
                    'new_class_average': new_version[i]["assignments"][j]["Class Average"]
                }

        if len(course_changes.keys()) > 1:
            changes.append(course_changes)

    return len(changes) > 0, changes


def send_notification(title: str, message: str):
    if desktop_notification:
        notification.notify(
            title=title,
            message=message,
            app_icon="icon.ico",
            timeout=5,
        )

    if mobile_notification:
        pass


def get_changes_message(changes: list) -> list:
    messages = []
    for change in changes:
        if 'new_assignments' in change:
            messages.append({
                'title': f"New assignments in {change['course_name']}",
                'message': f"Looks like your teacher opened a new assigment submission for"
                           f" {change['course_name']} course.\n"
            })
        if 'class_average_changed' in change and change['class_average_changed']['new_class_average'] == '-' \
                and change['class_average_changed']['new_class_average'] != '-':
            if messages[-1]['title'] != f"New assignments in {change['course_name']}":
                messages.pop()
            messages.append({
                'title': f"Class average changed in {change['course_name']}",
                'message': f"Looks like your teacher is publishing grades for assigment"
                           f" {change['class_average_changed']['assignment_name']} of {change['course_name']} course.\n"
            })
        if 'grades_changed' in change:
            if messages[-1]['title'] != f"New assignments in {change['course_name']}" or \
                    messages[-1]['title'] != f"Class average changed in {change['course_name']}":
                messages.pop()
            messages.append({
                'title': f"Grades changed in {change['course_name']}",
                'message': f"Looks like your teacher has changed your grade for assigment"
                           f" {change['grades_changed']['assignment_name']} of {change['course_name']} course.\n"
            })

    return messages


def check_for_updates():
    global session, _course_data, want_to_exit
    while not want_to_exit:
        if logged_in and session:
            if len(_course_data) == 0:
                _course_data = get_course_data()
            else:
                new_course_data = get_course_data()
                has_changes, changes = get_changes(_course_data, new_course_data)
                if has_changes:
                    messages = get_changes_message(changes)
                    for message in messages:
                        send_notification(message['title'], message['message'])
                    _course_data = new_course_data
    return


def background_tasks():
    threading.Thread(target=check_for_updates).start()
    return


def run():
    clear()
    user_interface_thread = threading.Thread(target=user_interface)
    user_interface_thread.start()

    background_thread = threading.Thread(target=background_tasks)
    background_thread.start()


def main():
    run()


if __name__ == "__main__":
    main()
