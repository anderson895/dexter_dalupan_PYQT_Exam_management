import sqlite3
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox, QRadioButton, QTableWidgetItem, QButtonGroup
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import QObject, QTimer, QTime, pyqtSignal
import datetime

# Global variable to store the current student's username
current_student_username = "1"


class TestTimer(QObject):
    time_updated = pyqtSignal(str)
    time_up = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.time_left = 3600  # 1 hour in seconds

    def start_timer(self):
        self.timer.start(1000)  # Update every second
        self.update_time()

    def update_time(self):
        self.time_left -= 1
        if self.time_left >= 0:
            time = QTime(0, 0, 0).addSecs(self.time_left).toString("hh:mm:ss")
            self.time_updated.emit(time)
        else:
            self.timer.stop()
            self.time_up.emit()

    def reset_timer(self):
        self.timer.stop()
        self.time_left = 3600  # Reset time to 1 hour

# Usage:
# Create an instance of TestTimer and start it when the test begins
# Connect the time_updated signal to update the time label in each test UI
# Connect the time_up signal to handle the end of the test


class LoginMain(QMainWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setWindowTitle("Login Main")
        loadUi("LoginMain.ui", self)
        self.stacked_widget = stacked_widget
        # Set the default size and make the window non-resizable
        self.stacked_widget.setFixedSize(500, 200)
        self.adminButton.clicked.connect(self.open_admin_login)
        self.studentButton.clicked.connect(self.open_student_login)

    def open_admin_login(self):
        self.stacked_widget.setCurrentIndex(1)  # Index of LoginAdmin in stackedWidget
        self.stacked_widget.setFixedSize(600, 600)

    def open_student_login(self):
        self.stacked_widget.setCurrentIndex(2)  # Index of LoginStudent in stackedWidget
        self.stacked_widget.setFixedSize(600, 600)


class LoginAdmin(QMainWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setWindowTitle("Login Admin")
        loadUi("LoginAdmin.ui", self)
        self.stacked_widget = stacked_widget
        # Set the default size and make the window non-resizable
        self.setFixedSize(600, 600)

        # Set echo mode for password line edit
        self.passwordLineEdit.setEchoMode(QLineEdit.EchoMode.Password)

        self.backButton.clicked.connect(self.go_back)  # Connect the back button to go_back method
        self.adminButton.clicked.connect(self.authenticate_admin)  # Connect login button to authentication method

    def go_back(self):
        self.stacked_widget.setCurrentIndex(0)  # Change the current widget to LoginMain
        self.stacked_widget.setFixedSize(500, 200)
        self.clear_line_edits()

    def authenticate_admin(self):
        username = self.usernameLineEdit.text()
        password = self.passwordLineEdit.text()

        if self.check_admin_credentials(username, password):
            QMessageBox.information(self, "Success", "Admin Login Successful")
            # Add code here to perform actions after successful login
            self.clear_line_edits()
            self.stacked_widget.setCurrentIndex(3)
            self.stacked_widget.setFixedSize(1280, 800)
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password")

    def check_admin_credentials(self, username, password):
        # Connect to SQLite database
        connection = sqlite3.connect("ExamDb.db")
        cursor = connection.cursor()

        # Query database to check if credentials exist
        cursor.execute("SELECT * FROM Admin WHERE username = ? AND password = ?", (username, password))
        admin = cursor.fetchone()

        # Close database connection
        connection.close()

        return admin is not None

    # Clear the line edits
    def clear_line_edits(self):
        self.usernameLineEdit.clear()
        self.passwordLineEdit.clear()


class LoginStudent(QMainWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setWindowTitle("Login Student")
        loadUi("LoginStudent.ui", self)
        self.stacked_widget = stacked_widget
        # Set the default size and make the window non-resizable
        self.setFixedSize(600, 600)

        self.test_timer = TestTimer()

        # Set echo mode for password line edit
        self.passwordLineEdit.setEchoMode(QLineEdit.EchoMode.Password)

        self.backButton.clicked.connect(self.go_back)  # Connect the back button to go_back method
        self.studentButton.clicked.connect(self.authenticate_student)  # Connect login button to authentication method

    def go_back(self):
        self.stacked_widget.setCurrentIndex(0)  # Change the current widget to LoginMain
        self.stacked_widget.setFixedSize(500, 200)
        self.clear_line_edits()

    def authenticate_student(self):
        username = self.usernameLineEdit.text()
        password = self.passwordLineEdit.text()

        if self.check_credentials(username, password):
            QMessageBox.information(self, "Success", "Student Login Successful")
            self.clear_line_edits()
            global current_student_username
            current_student_username = username
            self.stacked_widget.setCurrentIndex(8)  # Move to Reminder
            self.stacked_widget.setFixedSize(800, 600)
        else:
            QMessageBox.warning(self, "Authentication Failed", "Invalid username or password.")

    def check_credentials(self, username, password):
        connection = sqlite3.connect("ExamDb.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Students WHERE username=? AND password=?", (username, password))
        if cursor.fetchone():
            connection.close()
            return True
        connection.close()
        return False

    # Clear the line edits
    def clear_line_edits(self):
        self.usernameLineEdit.clear()
        self.passwordLineEdit.clear()


class AdminDashboard(QMainWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setWindowTitle("Admin Dashboard")
        loadUi("AdminDashboard.ui", self)
        self.stacked_widget = stacked_widget
        self.setFixedSize(1280, 800)

        self.addButton.clicked.connect(self.go_to_admin_add)
        self.editButton.clicked.connect(self.go_to_admin_edit)
        self.removeButton.clicked.connect(self.go_to_admin_remove)
        self.examResultsButton.clicked.connect(self.go_to_admin_view)
        self.logoutButton.clicked.connect(self.logout)

        # Update date and time label
        self.update_date_time_label()

        # Update number of students label
        self.update_number_of_students()

        # Update number of students who took the exam label
        self.update_number_of_takes()

        # Start a timer to update the time label every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_date_time_label)
        self.timer.start(1000)  # Update every 1000 milliseconds (1 second)

    def showEvent(self, event):
        super().showEvent(event)
        self.update_number_of_students()
        self.update_number_of_takes()

    def go_to_admin_add(self):
        self.stacked_widget.setCurrentIndex(4)
        self.stacked_widget.setFixedSize(1280, 800)

    def go_to_admin_edit(self):
        self.stacked_widget.setCurrentIndex(5)
        self.stacked_widget.setFixedSize(1280, 800)

    def go_to_admin_remove(self):
        self.stacked_widget.setCurrentIndex(6)
        self.stacked_widget.setFixedSize(1280, 800)

    def go_to_admin_view(self):
        self.stacked_widget.setCurrentIndex(7)
        self.stacked_widget.setFixedSize(1280, 800)

    def logout(self):
        self.stacked_widget.setCurrentIndex(0)
        self.stacked_widget.setFixedSize(500, 200)

    def update_date_time_label(self):
        # Get current date and time
        current_date_time = datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")  # 12-hour format with AM/PM
        self.dateTimeLabel.setText(current_date_time)

    def update_number_of_students(self):
        # Connect to the database
        connection = sqlite3.connect("ExamDb.db")
        cursor = connection.cursor()

        # Fetch the number of students registered
        cursor.execute("SELECT COUNT(*) FROM Students")
        num_students = cursor.fetchone()[0]

        # Update the label
        self.noOfStudents.setText(str(num_students))

        # Close the database connection
        connection.close()

    def update_number_of_takes(self):
        # Connect to the database
        connection = sqlite3.connect("ExamDb.db")
        cursor = connection.cursor()

        # Fetch the number of students who took the exam
        cursor.execute("SELECT COUNT(*) FROM Students WHERE overallscore IS NOT NULL")
        num_takes = cursor.fetchone()[0]

        # Update the label
        self.noOfTakes.setText(str(num_takes))

        # Close the database connection
        connection.close()


class AdminAdd(QMainWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setWindowTitle("Admin Add")
        loadUi("AdminAdd.ui", self)
        self.stacked_widget = stacked_widget
        self.setFixedSize(1280, 800)

        self.dashboardButton.clicked.connect(self.go_to_admin_dashboard)
        self.editButton.clicked.connect(self.go_to_admin_edit)
        self.removeButton.clicked.connect(self.go_to_admin_remove)
        self.examResultsButton.clicked.connect(self.go_to_admin_view)
        self.logoutButton.clicked.connect(self.logout)

        self.addToDb.clicked.connect(self.add_student_to_db)

        # Load students into the tableWidget
        self.load_students()

    def showEvent(self, event):
        super().showEvent(event)  # Call the parent class's showEvent method
        self.load_students()  # Update the table

    def go_to_admin_dashboard(self):
        self.stacked_widget.setCurrentIndex(3)
        self.stacked_widget.setFixedSize(1280, 800)
        self.clear_line_edits()

    def go_to_admin_edit(self):
        self.stacked_widget.setCurrentIndex(5)
        self.stacked_widget.setFixedSize(1280, 800)
        self.clear_line_edits()

    def go_to_admin_remove(self):
        self.stacked_widget.setCurrentIndex(6)
        self.stacked_widget.setFixedSize(1280, 800)
        self.clear_line_edits()

    def go_to_admin_view(self):
        self.stacked_widget.setCurrentIndex(7)
        self.stacked_widget.setFixedSize(1280, 800)
        self.clear_line_edits()

    def logout(self):
        self.stacked_widget.setCurrentIndex(0)
        self.stacked_widget.setFixedSize(500, 200)
        self.clear_line_edits()

    def load_students(self):
        # Connect to the database
        connection = sqlite3.connect("ExamDb.db")
        cursor = connection.cursor()

        # Fetch data from the Students table
        cursor.execute("SELECT id, fullname, age, course, username, password FROM Students")
        students_data = cursor.fetchall()

        # Populate the tableWidget with student data
        self.tableWidget.setRowCount(len(students_data))
        self.tableWidget.setColumnCount(6)  # Assuming there are 6 columns in the Students table

        for row_idx, student in enumerate(students_data):
            for col_idx, data in enumerate(student):
                item = QTableWidgetItem(str(data))
                self.tableWidget.setItem(row_idx, col_idx, item)

        # Close the connection
        connection.close()

    def add_student_to_db(self):
        # Retrieve data from line edits
        student_id = self.studentIdLine.text()
        full_name = self.fullNameLine.text()
        age = self.ageLine.text()
        course = self.courseLine.text()
        username = self.usernameLine.text()
        password = self.passwordLine.text()

        # Input validation
        if not all([student_id, full_name, age, course, username, password]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        # Check if the username or ID already exists for another student
        connection = sqlite3.connect("ExamDb.db")
        cursor = connection.cursor()
        cursor.execute("SELECT id, username FROM Students WHERE id = ? OR username = ?", (student_id, username))
        existing_student = cursor.fetchone()
        if existing_student:
            existing_id, existing_username = existing_student
            if existing_id == student_id:
                QMessageBox.warning(self, "Duplicate Error", "ID already exists for another student.")
            elif existing_username == username:
                QMessageBox.warning(self, "Duplicate Error", "Username already exists for another student.")
            connection.close()
            return

        # Add the student to the database
        try:
            cursor.execute("INSERT INTO Students (id, fullname, age, course, username, password) VALUES (?, ?, ?, ?, ?, ?)",
                           (student_id, full_name, age, course, username, password))
            connection.commit()
            QMessageBox.information(self, "Success", "Student added successfully.")
            self.load_students()  # Update the table
            self.clear_line_edits()  # Clear the line edits
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add student: {e}")
        finally:
            connection.close()

    def clear_line_edits(self):
        # Clear all line edits
        self.studentIdLine.clear()
        self.fullNameLine.clear()
        self.ageLine.clear()
        self.courseLine.clear()
        self.usernameLine.clear()
        self.passwordLine.clear()
        # Also clear tableWidget selection
        self.tableWidget.clearSelection()


class AdminEdit(QMainWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setWindowTitle("Admin Edit")
        loadUi("AdminEdit.ui", self)
        self.stacked_widget = stacked_widget
        self.setFixedSize(1280, 800)

        self.dashboardButton.clicked.connect(self.go_to_admin_dashboard)
        self.addButton.clicked.connect(self.go_to_admin_add)
        self.removeButton.clicked.connect(self.go_to_admin_remove)
        self.examResultsButton.clicked.connect(self.go_to_admin_view)
        self.logoutButton.clicked.connect(self.logout)

        self.editToDb.clicked.connect(self.edit_student_in_db)
        self.editToDb.setEnabled(False)  # Initially disable editToDb button

        # Load students into the tableWidget
        self.load_students()

        # Connect the itemSelectionChanged signal to the method that loads data into lineEdits
        self.tableWidget.itemSelectionChanged.connect(self.load_selected_student_data)

        # Initially, make line edits read-only
        self.set_line_edit_read_only(True)

    def showEvent(self, event):
        super().showEvent(event)  # Call the parent class's showEvent method
        self.load_students()  # Update the table

    def go_to_admin_dashboard(self):
        self.stacked_widget.setCurrentIndex(3)
        self.stacked_widget.setFixedSize(1280, 800)
        self.clear_line_edits()

    def go_to_admin_add(self):
        self.stacked_widget.setCurrentIndex(4)
        self.stacked_widget.setFixedSize(1280, 800)
        self.clear_line_edits()

    def go_to_admin_remove(self):
        self.stacked_widget.setCurrentIndex(6)
        self.stacked_widget.setFixedSize(1280, 800)
        self.clear_line_edits()

    def go_to_admin_view(self):
        self.stacked_widget.setCurrentIndex(7)
        self.stacked_widget.setFixedSize(1280, 800)
        self.clear_line_edits()

    def logout(self):
        self.stacked_widget.setCurrentIndex(0)
        self.stacked_widget.setFixedSize(500, 200)
        self.clear_line_edits()

    def load_students(self):
        # Connect to the database
        connection = sqlite3.connect("ExamDb.db")
        cursor = connection.cursor()

        # Fetch data from the Students table
        cursor.execute("SELECT id, fullname, age, course, username, password FROM Students")
        students_data = cursor.fetchall()

        # Populate the tableWidget with student data
        self.tableWidget.setRowCount(len(students_data))
        self.tableWidget.setColumnCount(6)  # Assuming there are 6 columns in the Students table

        for row_idx, student in enumerate(students_data):
            for col_idx, data in enumerate(student):
                item = QTableWidgetItem(str(data))
                self.tableWidget.setItem(row_idx, col_idx, item)

        # Close the connection
        connection.close()

    def load_selected_student_data(self):
        selected_row = self.tableWidget.currentRow()
        if selected_row != -1:
            # Retrieve data from the selected row
            student_id = self.tableWidget.item(selected_row, 0).text()
            full_name = self.tableWidget.item(selected_row, 1).text()
            age = self.tableWidget.item(selected_row, 2).text()
            course = self.tableWidget.item(selected_row, 3).text()
            username = self.tableWidget.item(selected_row, 4).text()
            password = self.tableWidget.item(selected_row, 5).text()

            # Enable editToDb button and make line edits editable
            self.editToDb.setEnabled(True)
            self.set_line_edit_read_only(False)

            # Display data in line edits
            self.studentIdLine.setText(student_id)
            self.fullNameLine.setText(full_name)
            self.ageLine.setText(age)
            self.courseLine.setText(course)
            self.usernameLine.setText(username)
            self.passwordLine.setText(password)
        else:
            # If no row is selected, disable editToDb button and make line edits read-only
            self.editToDb.setEnabled(False)
            self.set_line_edit_read_only(True)

    def edit_student_in_db(self):
        # Retrieve edited data from line edits
        student_id = self.studentIdLine.text()
        full_name = self.fullNameLine.text()
        age = self.ageLine.text()
        course = self.courseLine.text()
        username = self.usernameLine.text()
        password = self.passwordLine.text()

        # Input validation
        if not all([student_id, full_name, age, course, username, password]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        # Check if the username or ID already exists for another student
        connection = sqlite3.connect("ExamDb.db")
        cursor = connection.cursor()
        cursor.execute("SELECT id, username FROM Students WHERE (id != ? OR username != ?) AND (username = ? OR id = ?)",
                       (student_id, username, username, student_id))
        existing_student = cursor.fetchone()
        if existing_student:
            QMessageBox.warning(self, "Duplicate Error", "Username or ID already exists for another student.")
            connection.close()
            return

        # Update the student in the database
        try:
            cursor.execute("UPDATE Students SET id = ?, fullname = ?, age = ?, course = ?, username = ?, password = ? WHERE id = ?",
                           (student_id, full_name, age, course, username, password, student_id))
            connection.commit()
            QMessageBox.information(self, "Success", "Student information updated successfully.")
            self.load_students()  # Update the table
            self.clear_line_edits()  # Clear the line edits
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Database Error", f"Failed to update student information: {e}")
        finally:
            connection.close()

    def clear_line_edits(self):
        # Clear all line edits
        self.studentIdLine.clear()
        self.fullNameLine.clear()
        self.ageLine.clear()
        self.courseLine.clear()
        self.usernameLine.clear()
        self.passwordLine.clear()
        # Also clear tableWidget selection
        self.tableWidget.clearSelection()

    def set_line_edit_read_only(self, read_only):
        # Function to set line edits read-only or editable
        self.studentIdLine.setReadOnly(read_only)
        self.fullNameLine.setReadOnly(read_only)
        self.ageLine.setReadOnly(read_only)
        self.courseLine.setReadOnly(read_only)
        self.usernameLine.setReadOnly(read_only)
        self.passwordLine.setReadOnly(read_only)


class AdminRemove(QMainWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setWindowTitle("Admin Remove")
        loadUi("AdminRemove.ui", self)
        self.stacked_widget = stacked_widget
        self.setFixedSize(1280, 800)

        self.dashboardButton.clicked.connect(self.go_to_admin_dashboard)
        self.addButton.clicked.connect(self.go_to_admin_add)
        self.editButton.clicked.connect(self.go_to_admin_edit)
        self.examResultsButton.clicked.connect(self.go_to_admin_view)
        self.logoutButton.clicked.connect(self.logout)

        self.removeFromDb.clicked.connect(self.remove_student_from_db)

        # Load students into the tableWidget
        self.load_students()

        # Clear labels initially
        self.clear_labels()

        # Connect tableWidget item selection event to show_student_details method
        self.tableWidget.itemSelectionChanged.connect(self.show_student_details)

    def showEvent(self, event):
        super().showEvent(event)  # Call the parent class's showEvent method
        self.load_students()  # Update the table

    def go_to_admin_dashboard(self):
        self.stacked_widget.setCurrentIndex(3)
        self.stacked_widget.setFixedSize(1280, 800)
        self.clear_labels()

    def go_to_admin_add(self):
        self.stacked_widget.setCurrentIndex(4)
        self.stacked_widget.setFixedSize(1280, 800)
        self.clear_labels()

    def go_to_admin_edit(self):
        self.stacked_widget.setCurrentIndex(5)
        self.stacked_widget.setFixedSize(1280, 800)
        self.clear_labels()

    def go_to_admin_view(self):
        self.stacked_widget.setCurrentIndex(7)
        self.stacked_widget.setFixedSize(1280, 800)
        self.clear_labels()

    def logout(self):
        self.stacked_widget.setCurrentIndex(0)
        self.stacked_widget.setFixedSize(500, 200)
        self.clear_labels()

    def load_students(self):
        # Connect to the database
        connection = sqlite3.connect("ExamDb.db")
        cursor = connection.cursor()

        # Fetch data from the Students table
        cursor.execute("SELECT id, fullname, age, course, username, password FROM Students")
        students_data = cursor.fetchall()

        # Populate the tableWidget with student data
        self.tableWidget.setRowCount(len(students_data))
        self.tableWidget.setColumnCount(6)  # Assuming there are 6 columns in the Students table

        for row_idx, student in enumerate(students_data):
            for col_idx, data in enumerate(student):
                item = QTableWidgetItem(str(data))
                self.tableWidget.setItem(row_idx, col_idx, item)

        # Close the connection
        connection.close()

    def remove_student_from_db(self):
        # Get the selected row
        selected_row = self.tableWidget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "No Selection", "Please select a student to remove.")
            return

        # Get the ID of the selected student
        student_id = self.tableWidget.item(selected_row, 0).text()

        # Confirm removal
        reply = QMessageBox.question(self, "Confirmation", "Are you sure you want to remove this student?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        if reply == QMessageBox.StandardButton.Yes:
            # Connect to the database
            connection = sqlite3.connect("ExamDb.db")
            cursor = connection.cursor()

            # Remove the student from the database
            try:
                cursor.execute("DELETE FROM Students WHERE id = ?", (student_id,))
                connection.commit()
                QMessageBox.information(self, "Success", "Student removed successfully.")
                self.load_students()  # Update the table
                self.clear_labels()  # Clear labels
            except sqlite3.Error as e:
                QMessageBox.warning(self, "Database Error", f"Failed to remove student: {e}")
            finally:
                connection.close()

    def clear_labels(self):
        # Clear all labels
        self.studentIdLabel.clear()
        self.fullnameLabel.clear()
        self.ageLabel.clear()
        self.courseLabel.clear()
        self.usernameLabel.clear()
        self.passwordLabel.clear()
        # Also clear tableWidget selection
        self.tableWidget.clearSelection()

    def show_student_details(self):
        # Get the selected row
        selected_row = self.tableWidget.currentRow()
        if selected_row == -1:
            return

        # Get data from the selected row
        student_id = self.tableWidget.item(selected_row, 0).text()
        fullname = self.tableWidget.item(selected_row, 1).text()
        age = self.tableWidget.item(selected_row, 2).text()
        course = self.tableWidget.item(selected_row, 3).text()
        username = self.tableWidget.item(selected_row, 4).text()
        password = self.tableWidget.item(selected_row, 5).text()

        # Display data in labels
        self.studentIdLabel.setText(student_id)
        self.fullnameLabel.setText(fullname)
        self.ageLabel.setText(age)
        self.courseLabel.setText(course)
        self.usernameLabel.setText(username)
        self.passwordLabel.setText(password)


class AdminView(QMainWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setWindowTitle("Admin View")
        loadUi("AdminView.ui", self)
        self.stacked_widget = stacked_widget
        self.setFixedSize(1280, 800)

        self.dashboardButton.clicked.connect(self.go_to_admin_dashboard)
        self.addButton.clicked.connect(self.go_to_admin_add)
        self.editButton.clicked.connect(self.go_to_admin_edit)
        self.removeButton.clicked.connect(self.go_to_admin_remove)
        self.logoutButton.clicked.connect(self.logout)

        # Load students into the tableWidget
        self.load_students()

    def showEvent(self, event):
        super().showEvent(event)  # Call the parent class's showEvent method
        self.load_students()  # Update the table

    def go_to_admin_dashboard(self):
        self.stacked_widget.setCurrentIndex(3)
        self.stacked_widget.setFixedSize(1280, 800)
        self.clear_table_selection()

    def go_to_admin_add(self):
        self.stacked_widget.setCurrentIndex(4)
        self.stacked_widget.setFixedSize(1280, 800)
        self.clear_table_selection()

    def go_to_admin_edit(self):
        self.stacked_widget.setCurrentIndex(5)
        self.stacked_widget.setFixedSize(1280, 800)
        self.clear_table_selection()

    def go_to_admin_remove(self):
        self.stacked_widget.setCurrentIndex(6)
        self.stacked_widget.setFixedSize(1280, 800)
        self.clear_table_selection()

    def logout(self):
        self.stacked_widget.setCurrentIndex(0)
        self.stacked_widget.setFixedSize(500, 200)
        self.clear_table_selection()

    def load_students(self):
        # Connect to the database
        connection = sqlite3.connect("ExamDb.db")
        cursor = connection.cursor()

        # Fetch data from the Students table
        cursor.execute("SELECT id, fullname, course, test1, test2, test3, test4, test5, overallscore FROM Students")
        students_data = cursor.fetchall()

        # Populate the tableWidget with student data
        self.tableWidget.setRowCount(len(students_data))
        self.tableWidget.setColumnCount(9)  # Assuming there are 9 columns in the Students table

        for row_idx, student in enumerate(students_data):
            for col_idx, data in enumerate(student):
                item = QTableWidgetItem(str(data))
                self.tableWidget.setItem(row_idx, col_idx, item)

        # Close the connection
        connection.close()

    # clear the tableWidget selection
    def clear_table_selection(self):
        self.tableWidget.clearSelection()


class Reminder(QMainWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setWindowTitle("Reminder")
        loadUi("Reminder.ui", self)
        self.stacked_widget = stacked_widget
        self.setFixedSize(800, 600)
        self.startButton.clicked.connect(self.start_test)

    def start_test(self):
        self.stacked_widget.setCurrentIndex(9)  # Move to Test 1
        self.stacked_widget.setFixedSize(600, 600)


class Test1(QMainWindow):
    def __init__(self, stacked_widget, test_timer):
        super().__init__()
        self.setWindowTitle("Test 1")
        loadUi("Test1.ui", self)
        self.stacked_widget = stacked_widget
        self.test_timer = test_timer
        self.setFixedSize(600, 600)
        self.current_question_index = 0
        self.answers = []

        # Create a QButtonGroup
        self.button_group = QButtonGroup(self)

        # Add radio buttons to the group
        self.button_group.addButton(self.choice1)
        self.button_group.addButton(self.choice2)
        self.button_group.addButton(self.choice3)
        self.button_group.addButton(self.choice4)

        # Load questions and choices
        self.load_questions()

        # Connect nextButton to load_next_question method
        self.nextButton.clicked.connect(self.load_next_question)

        # Connect timer signals
        self.test_timer.time_updated.connect(self.update_time)
        self.test_timer.time_up.connect(self.handle_time_up)

        # Start the timer
        self.test_timer.start_timer()

    def update_time(self, time):
        self.timeLabel.setText(f"Time Left: {time}")

    def handle_time_up(self):
        QMessageBox.information(self, "Time's Up", "The test time has ended.")
        # Add code to handle the end of the test here
        self.compare_answers()

    def load_questions(self):
        connection = sqlite3.connect("ExamDb.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Test1")
        self.questions = cursor.fetchall()
        connection.close()
        self.display_question()

    def display_question(self):
        if self.current_question_index < len(self.questions):
            question_data = self.questions[self.current_question_index]
            self.questionNumberLabel.setText(f"Question {self.current_question_index + 1}")
            self.questionLabel.setText(question_data[0])
            self.choice1.setText(question_data[1])
            self.choice2.setText(question_data[2])
            self.choice3.setText(question_data[3])
            self.choice4.setText(question_data[4])
            self.reset_radio_buttons()
        else:
            QMessageBox.information(self, "End of Test", "You have completed test 1.")
            self.stacked_widget.setCurrentIndex(10)  # Move to Test 2
            self.stacked_widget.setFixedSize(600, 600)
            # Compare answers at the end of the test
            self.compare_answers()

    def load_next_question(self):
        if self.selected_answer():
            self.answers.append(self.get_selected_choice())
            self.reset_radio_buttons()
            self.current_question_index += 1
            self.display_question()
        else:
            QMessageBox.warning(self, "Warning", "Please select an answer before proceeding.")

    def reset_radio_buttons(self):
        for button in self.findChildren(QRadioButton):
            button.setChecked(False)

    def selected_answer(self):
        return any(button.isChecked() for button in self.findChildren(QRadioButton))

    def get_selected_choice(self):
        choices = [self.choice1, self.choice2, self.choice3, self.choice4]
        for idx, choice in enumerate(choices, start=1):
            if choice.isChecked():
                return str(idx)
        return None

    def compare_answers(self):
        connection = sqlite3.connect("ExamDb.db")
        cursor = connection.cursor()
        correct_answers = []
        cursor.execute("SELECT correctanswer FROM Test1")
        correct_answers = [ans[0] for ans in cursor.fetchall()]
        connection.close()

        score = 0
        for i, ans in enumerate(self.answers):
            if ans == correct_answers[i]:
                score += 1

        # Update the student's test1 score in the database using the global variable
        connection = sqlite3.connect("ExamDb.db")
        cursor = connection.cursor()
        cursor.execute("UPDATE Students SET test1 = ? WHERE username = ?", (score, current_student_username))
        connection.commit()
        connection.close()


class Test2(QMainWindow):
    def __init__(self, stacked_widget, test_timer):
        super().__init__()
        self.setWindowTitle("Test 2")
        loadUi("Test2.ui", self)
        self.stacked_widget = stacked_widget
        self.test_timer = test_timer
        self.setFixedSize(600, 600)
        self.current_question_index = 0
        self.answers = []  # Store student's answers

        # Load questions
        self.load_questions()

        # Connect nextButton to load_next_question method
        self.nextButton.clicked.connect(self.load_next_question)

        # Connect timer signals
        self.test_timer.time_updated.connect(self.update_time)
        self.test_timer.time_up.connect(self.handle_time_up)

        # Start the timer
        self.test_timer.start_timer()

    def update_time(self, time):
        self.timeLabel.setText(f"Time Left: {time}")

    def handle_time_up(self):
        QMessageBox.information(self, "Time's Up", "The test time has ended.")
        # Add code to handle the end of the test here
        self.compare_answers()

    def load_questions(self):
        connection = sqlite3.connect("ExamDb.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Test2")
        self.questions = cursor.fetchall()
        connection.close()
        self.display_question()

    def display_question(self):
        if self.current_question_index < len(self.questions):
            question_data = self.questions[self.current_question_index]
            self.questionNumberLabel.setText(f"Question {self.current_question_index + 1}")
            self.questionLabel.setText(question_data[0])
            self.textAnswer.clear()  # Clear the previous answer
        else:
            QMessageBox.information(self, "End of Test", "You have completed test 2.")
            self.stacked_widget.setCurrentIndex(11)  # Move to Test 3
            self.stacked_widget.setFixedSize(600, 600)
            self.compare_answers()

    def load_next_question(self):
        answer = self.textAnswer.text().strip()
        if not answer:
            QMessageBox.warning(self, "Warning", "Please enter an answer before proceeding.")
            return

        self.current_question_index += 1
        self.answers.append(answer)  # Store the student's answer
        self.display_question()

    def compare_answers(self):
        connection = sqlite3.connect("ExamDb.db")
        cursor = connection.cursor()
        correct_answers = []
        cursor.execute("SELECT correctanswer FROM Test2")
        correct_answers = [ans[0] for ans in cursor.fetchall()]
        connection.close()

        score = 0
        for i, ans in enumerate(self.answers):
            if ans == correct_answers[i]:
                score += 1

        # Update the student's test2 score in the database using the global variable
        connection = sqlite3.connect("ExamDb.db")
        cursor = connection.cursor()
        cursor.execute("UPDATE Students SET test2 = ? WHERE username = ?", (score, current_student_username))
        connection.commit()
        connection.close()


class Test3(QMainWindow):
    def __init__(self, stacked_widget, test_timer):
        super().__init__()
        self.setWindowTitle("Test 3")
        loadUi("Test3.ui", self)
        self.stacked_widget = stacked_widget
        self.test_timer = test_timer
        self.setFixedSize(600, 600)
        self.current_question_index = 0
        self.answers = []  # Store student's answers

        # Load questions
        self.load_questions()

        # Connect nextButton to load_next_question method
        self.nextButton.clicked.connect(self.load_next_question)

        # Connect timer signals
        self.test_timer.time_updated.connect(self.update_time)
        self.test_timer.time_up.connect(self.handle_time_up)

        # Start the timer
        self.test_timer.start_timer()

    def update_time(self, time):
        self.timeLabel.setText(f"Time Left: {time}")

    def handle_time_up(self):
        QMessageBox.information(self, "Time's Up", "The test time has ended.")
        # Add code to handle the end of the test here
        self.compare_answers()

    def load_questions(self):
        connection = sqlite3.connect("ExamDb.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Test3")
        self.questions = cursor.fetchall()
        connection.close()
        self.display_question()

    def display_question(self):
        if self.current_question_index < len(self.questions):
            question_data = self.questions[self.current_question_index]
            self.questionNumberLabel.setText(f"Question {self.current_question_index + 1}")
            self.questionLabel.setText(question_data[0])
            # Since the choices are True or False, we can directly set them
            self.choice1.setText("True")
            self.choice2.setText("False")
            self.reset_radio_buttons()
        else:
            QMessageBox.information(self, "End of Test", "You have completed test 3.")
            # Add code to handle completion of Test3
            self.stacked_widget.setCurrentIndex(12)  # Move to Test 4
            self.stacked_widget.setFixedSize(600, 600)
            self.compare_answers()

    def load_next_question(self):
        if self.selected_answer():
            self.current_question_index += 1
            selected_choice = "True" if self.choice1.isChecked() else "False"
            self.answers.append(selected_choice.lower())  # Store the lowercase of the selected choice
            self.display_question()
        else:
            QMessageBox.warning(self, "Warning", "Please select an answer before proceeding.")

    def reset_radio_buttons(self):
        for button in self.findChildren(QRadioButton):
            button.setChecked(False)

    def selected_answer(self):
        return any(button.isChecked() for button in self.findChildren(QRadioButton))

    def compare_answers(self):
        connection = sqlite3.connect("ExamDb.db")
        cursor = connection.cursor()
        correct_answers = []
        cursor.execute("SELECT correctanswer FROM Test3")
        correct_answers = [row[0].lower() for row in cursor.fetchall()]  # Convert correct answers to lowercase
        connection.close()

        score = 0
        for i, ans in enumerate(self.answers):
            if ans == correct_answers[i]:
                score += 1

        # Update the student's test3 score in the database using the global variable
        connection = sqlite3.connect("ExamDb.db")
        cursor = connection.cursor()
        cursor.execute("UPDATE Students SET test3 = ? WHERE username = ?", (score, current_student_username))
        connection.commit()
        connection.close()


class Test4(QMainWindow):
    def __init__(self, stacked_widget, test_timer):
        super().__init__()
        self.setWindowTitle("Test 4")
        loadUi("Test4.ui", self)
        self.stacked_widget = stacked_widget
        self.test_timer = test_timer
        self.setFixedSize(600, 600)
        self.current_question_index = 0
        self.answers = []  # Store student's answers

        # Load questions and choices
        self.load_questions()

        # Connect nextButton to load_next_question method
        self.nextButton.clicked.connect(self.load_next_question)

        # Connect timer signals
        self.test_timer.time_updated.connect(self.update_time)
        self.test_timer.time_up.connect(self.handle_time_up)

        # Start the timer
        self.test_timer.start_timer()

    def update_time(self, time):
        self.timeLabel.setText(f"Time Left: {time}")

    def handle_time_up(self):
        QMessageBox.information(self, "Time's Up", "The test time has ended.")
        # Add code to handle the end of the test here
        self.compare_answers()

    def load_questions(self):
        connection = sqlite3.connect("ExamDb.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Test4")
        self.questions = cursor.fetchall()
        connection.close()
        self.display_question()

    def display_question(self):
        if self.current_question_index < len(self.questions):
            question_data = self.questions[self.current_question_index]
            self.questionNumberLabel.setText(f"Question {self.current_question_index + 1}")
            self.questionLabel.setText(question_data[0])
            self.choice1.setText(question_data[1])
            self.choice2.setText(question_data[2])
            self.choice3.setText(question_data[3])
            self.choice4.setText(question_data[4])
            self.reset_radio_buttons()
        else:
            QMessageBox.information(self, "End of Test", "You have completed test 4.")
            # Transition to the next test or perform other actions
            self.stacked_widget.setCurrentIndex(13)  # Move to Test 5
            self.stacked_widget.setFixedSize(600, 600)
            self.compare_answers()

    def load_next_question(self):
        if self.selected_answer():
            self.current_question_index += 1
            self.answers.append(self.get_selected_choice())  # Store the student's answer
            self.display_question()
        else:
            QMessageBox.warning(self, "Warning", "Please select an answer before proceeding.")

    def reset_radio_buttons(self):
        for button in self.findChildren(QRadioButton):
            button.setChecked(False)

    def selected_answer(self):
        return any(button.isChecked() for button in self.findChildren(QRadioButton))

    def get_selected_choice(self):
        choices = [self.choice1, self.choice2, self.choice3, self.choice4]
        for idx, choice in enumerate(choices, start=1):
            if choice.isChecked():
                return str(idx)
        return None

    def compare_answers(self):
        connection = sqlite3.connect("ExamDb.db")
        cursor = connection.cursor()
        correct_answers = []
        cursor.execute("SELECT * FROM Test4")
        correct_answers = [row[5] for row in cursor.fetchall()]  # Assuming the correct answers are in the 6th column
        connection.close()

        score = 0
        for i, ans in enumerate(self.answers):
            if ans == correct_answers[i]:
                score += 1

        # Update the student's test4 score in the database using the global variable
        connection = sqlite3.connect("ExamDb.db")
        cursor = connection.cursor()
        cursor.execute("UPDATE Students SET test4 = ? WHERE username = ?", (score, current_student_username))
        connection.commit()
        connection.close()


class Test5(QMainWindow):
    def __init__(self, stacked_widget, test_timer):
        super().__init__()
        self.setWindowTitle("Test 5")
        loadUi("Test5.ui", self)
        self.stacked_widget = stacked_widget
        self.test_timer = test_timer
        self.setFixedSize(600, 600)
        self.current_question_index = 0
        self.answers = []  # Store student's answers

        # Load questions
        self.load_questions()

        # Connect nextButton to load_next_question method
        self.nextButton.clicked.connect(self.load_next_question)

        # Connect timer signals
        self.test_timer.time_updated.connect(self.update_time)
        self.test_timer.time_up.connect(self.handle_time_up)

        # Start the timer
        self.test_timer.start_timer()

    def update_time(self, time):
        self.timeLabel.setText(f"Time Left: {time}")

    def handle_time_up(self):
        QMessageBox.information(self, "Time's Up", "The test time has ended.")
        # Add code to handle the end of the test here
        self.go_to_results()
        self.compare_answers()

    def go_to_results(self):
        results = Results(self.stacked_widget)
        self.stacked_widget.addWidget(results)
        self.stacked_widget.setCurrentIndex(self.stacked_widget.count() - 1)
        self.stacked_widget.setFixedSize(600, 500)

    def load_questions(self):
        connection = sqlite3.connect("ExamDb.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Test5")
        self.questions = cursor.fetchall()
        connection.close()
        self.display_question()

    def display_question(self):
        if self.current_question_index < len(self.questions):
            question_data = self.questions[self.current_question_index]
            self.questionNumberLabel.setText(f"Question {self.current_question_index + 1}")
            self.questionLabel.setText(question_data[0])
            self.choice1.setText(question_data[1])
            self.choice2.setText(question_data[2])
            self.choice3.setText(question_data[3])
            self.choice4.setText(question_data[4])
            self.choice5.setText(question_data[5])
            self.reset_radio_buttons()
        else:
            QMessageBox.information(self, "End of Test", "You have completed test 5.")
            self.compare_answers()
            self.go_to_results()
            # Transition to the next test or perform other actions
            # self.stacked_widget.setCurrentIndex(13)  # Move to Results
            # self.stacked_widget.setFixedSize(600, 500)

    def load_next_question(self):
        if self.selected_answer():
            self.current_question_index += 1
            selected_choice = self.get_selected_choice()
            self.answers.append(selected_choice)
            self.reset_radio_buttons()
            self.display_question()
        else:
            QMessageBox.warning(self, "Warning", "Please select an answer before proceeding.")

    def reset_radio_buttons(self):
        for button in self.findChildren(QRadioButton):
            button.setChecked(False)

    def selected_answer(self):
        return any(button.isChecked() for button in self.findChildren(QRadioButton))

    def get_selected_choice(self):
        choices_mapping = {self.choice1: 'a', self.choice2: 'b', self.choice3: 'c', self.choice4: 'd', self.choice5: 'e'}
        for choice, letter in choices_mapping.items():
            if choice.isChecked():
                return letter
        return None

    def compare_answers(self):
        connection = sqlite3.connect("ExamDb.db")
        cursor = connection.cursor()
        cursor.execute("SELECT correctanswer FROM Test5")
        correct_answers = [row[0] for row in cursor.fetchall()]
        connection.close()

        score = 0
        for i, ans in enumerate(self.answers):
            if ans == correct_answers[i]:
                score += 1

        # Update the student's test5 score in the database using the global variable
        connection = sqlite3.connect("ExamDb.db")
        cursor = connection.cursor()
        cursor.execute("UPDATE Students SET test5 = ? WHERE username = ?", (score, current_student_username))
        connection.commit()
        connection.close()


class Results(QMainWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setWindowTitle("Results")
        loadUi("Results.ui", self)
        self.stacked_widget = stacked_widget
        self.setFixedSize(600, 500)

        # Connect continueButton to go_back_to_login method
        self.continueButton.clicked.connect(self.go_back_to_login)

        # Calculate and display test results
        overall_score = self.display_test_results()

        # Save overall score in the database
        if overall_score is not None:
            self.save_overall_score(overall_score)

    def display_test_results(self):
        connection = sqlite3.connect("ExamDb.db")
        cursor = connection.cursor()

        # Fetch test scores from the database
        cursor.execute("SELECT test1, test2, test3, test4, test5 FROM Students WHERE username = ?", (current_student_username,))
        test_scores = cursor.fetchone()
        connection.close()

        if test_scores is None:
            return None

        # Calculate overall score
        overall_score = sum(test_scores)

        # Display individual test scores
        tests = ["Test 1", "Test 2", "Test 3", "Test 4", "Test 5"]
        labels = [self.test1Result, self.test2Result, self.test3Result, self.test4Result, self.test5Result]
        for i in range(len(tests)):
            labels[i].setText(f"{tests[i]} = {test_scores[i]}/30")

        # Display overall score
        self.overallScore.setText(f"Overall Score = {overall_score}/150")

        return overall_score

    def save_overall_score(self, overall_score):
        connection = sqlite3.connect("ExamDb.db")
        cursor = connection.cursor()

        # Update overall score in the database
        cursor.execute("UPDATE Students SET overallscore = ? WHERE username = ?", (overall_score, current_student_username))
        connection.commit()
        connection.close()

    def go_back_to_login(self):
        self.stacked_widget.setCurrentIndex(0)  # Go back to LoginMain
        self.stacked_widget.setFixedSize(500, 200)


def main():
    app = QApplication([])
    stacked_widget = QStackedWidget()
    login_main = LoginMain(stacked_widget)
    login_admin = LoginAdmin(stacked_widget)
    login_student = LoginStudent(stacked_widget)
    admin_dashboard = AdminDashboard(stacked_widget)
    admin_add = AdminAdd(stacked_widget)
    admin_edit = AdminEdit(stacked_widget)
    admin_remove = AdminRemove(stacked_widget)
    admin_view = AdminView(stacked_widget)
    reminder = Reminder(stacked_widget)
    test_timer = TestTimer()
    test1 = Test1(stacked_widget, test_timer)
    test2 = Test2(stacked_widget, test_timer)
    test3 = Test3(stacked_widget, test_timer)
    test4 = Test4(stacked_widget, test_timer)
    test5 = Test5(stacked_widget, test_timer)
    # results = Results(stacked_widget)

    stacked_widget.addWidget(login_main)  # Index 0
    stacked_widget.addWidget(login_admin)  # Index 1
    stacked_widget.addWidget(login_student)  # Index 2
    stacked_widget.addWidget(admin_dashboard)  # Index 3
    stacked_widget.addWidget(admin_add)  # Index 4
    stacked_widget.addWidget(admin_edit)  # Index 5
    stacked_widget.addWidget(admin_remove)  # Index 6
    stacked_widget.addWidget(admin_view)  # Index 7
    stacked_widget.addWidget(reminder)  # Index 8
    stacked_widget.addWidget(test1)  # Index 9
    stacked_widget.addWidget(test2)  # Index 10
    stacked_widget.addWidget(test3)  # Index 11
    stacked_widget.addWidget(test4)  # Index 12
    stacked_widget.addWidget(test5)  # Index 13
    # stacked_widget.addWidget(results)  # Index 14

    stacked_widget.show()
    app.exec()


if __name__ == "__main__":
    main()
