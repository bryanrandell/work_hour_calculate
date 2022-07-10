from PyQt5.QtWidgets import (QWidget, QApplication, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QTextEdit,
                             QFileDialog, QMessageBox, QComboBox, QProgressDialog, QProgressBar, QCheckBox, QDialog)
from PyQt5.QtCore import Qt, QTimer, QThread, QObject, pyqtSignal, pyqtSlot
import sys
import json


def substract_end_time_from_start_time_list(start_time_list: list, end_time_list: list, pause_time: int = 1) -> list:
    week_work_hour_list = []
    for start, end in zip(start_time_list, end_time_list):
        # if start > end:
        #     raise ValueError("Start time is greater than end time")

        start_hour = int(start.split(":")[0])
        start_minute = int(start.split(":")[1])
        end_hour = int(end.split(":")[0])
        end_minute = int(end.split(":")[1])
        total_work_hour = (end_hour - start_hour) * 60 + (end_minute - start_minute)
        total_work_hour -= pause_time * 60
        convert_back_to_time = str(total_work_hour // 60) + ":" + str(total_work_hour % 60)
        week_work_hour_list.append(total_work_hour)

    return week_work_hour_list


def sum_hour_list(hour_list: list) -> str:
    sum_minutes = 0
    for hour in hour_list:
        hours = int(hour.split(":")[0]) * 60
        minutes = int(hour.split(":")[1])
        sum_minutes += hours
        sum_minutes += minutes
    return str(sum_minutes // 60) + ":" + str(sum_minutes % 60)


def substract_end_time_from_start_time(start: str, end: str, pause_time: str = "1") -> str:
    start_hour = int(start.split(":")[0])
    start_minute = int(start.split(":")[1])
    end_hour = int(end.split(":")[0])
    end_minute = int(end.split(":")[1])
    if start > end:
        total_work_hour = ((end_hour + 12) - start_hour) * 60 + (end_minute - start_minute)
    else:
        total_work_hour = (end_hour - start_hour) * 60 + (end_minute - start_minute)

    total_work_hour -= int(pause_time) * 60

    return str(total_work_hour // 60) + ":" + str(total_work_hour % 60)


def save_work_hour_to_json_file(work_hour_dict: dict, project_name: str, week_number: str) -> bool:
    with open(f'{project_name}_week_{week_number}.json', "w") as f:
        json.dump(work_hour_dict, f)
    return True


def load_work_hour_from_json_file(project_name: str, week_number: str) -> dict:
    with open(f'{project_name}_week_{week_number}.json', "r") as f:
        return json.load(f)


class PopUpSaveJson(QWidget):
    def __init__(self):
        super().__init__()
        self.work_hour_dict = {}
        self.project_name = "Cannes_Confidential"
        self.week_number = "01"
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Save work hour")
        self.setGeometry(300, 300, 300, 200)
        self.setFixedSize(300, 200)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: #f0f0f0;")

        self.label = QLabel("Save work hour to json file?", self)
        self.label.setGeometry(10, 10, 280, 20)
        self.label.setStyleSheet("font-size: 15px;")

        self.project_name_label = QLabel("Project name:", self)
        self.project_name_label.setGeometry(10, 40, 80, 20)
        self.project_name_line_edit = QLineEdit(self)
        self.project_name_line_edit.setText(self.project_name)
        self.project_name_line_edit.editingFinished.connect(self.edit_project)
        self.project_name_line_edit.setGeometry(100, 40, 180, 20)

        self.week_number_label = QLabel("Week number:", self)
        self.week_number_label.setGeometry(10, 70, 80, 20)
        self.week_number_line_edit = QLineEdit(self)
        self.week_number_line_edit.setText(self.week_number)
        self.week_number_line_edit.editingFinished.connect(self.edit_week)
        self.week_number_line_edit.setGeometry(100, 70, 180, 20)

        self.button_yes = QPushButton("Yes", self)
        self.button_yes.setGeometry(10, 50, 100, 30)
        self.button_yes.clicked.connect(self.save_work_hour_to_json_file)

        self.button_no = QPushButton("No", self)
        self.button_no.setGeometry(120, 50, 100, 30)
        # self.button_no.clicked.connect(self.close)

    # def close(self):
    #     self.destroy()

    def edit_week(self):
        self.week_number = self.week_number_line_edit.text()

    def edit_project(self):
        self.project_name = self.project_name_line_edit.text()

    def save_work_hour_to_json_file(self):
        save_work_hour_to_json_file(self.work_hour_dict, self.project_name, self.week_number)
        self.close()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Work Hour Calculator')
        # self.setFixedSize(400, 400)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.dict_line_edit_start = {}
        self.dict_line_edit_end = {}
        self.dict_line_pause_hour = {}
        self.dict_check_box = {}
        self.dict_label_work_hour = {}
        for day in self.weekdays:
            self.day_layout = QHBoxLayout()

            self.dict_check_box[day] = QCheckBox()
            if day == "Saturday" or day == "Sunday":
                self.dict_check_box[day].setChecked(False)
            else:
                self.dict_check_box[day].setChecked(True)
            self.day_layout.addWidget(self.dict_check_box[day])
            self.day_layout.addWidget(QLabel(day))
            self.day_layout.addWidget(QLabel("Start Time"))
            self.dict_line_edit_start[day] = QLineEdit()
            self.dict_line_edit_start[day].setText("00:00")
            self.dict_line_edit_start[day].setFixedWidth(50)
            self.day_layout.addWidget(self.dict_line_edit_start[day])
            self.day_layout.addWidget(QLabel("End Time"))
            self.dict_line_edit_end[day] = QLineEdit()
            self.dict_line_edit_end[day].setText("00:00")
            self.dict_line_edit_end[day].setFixedWidth(50)
            self.day_layout.addWidget(self.dict_line_edit_end[day])
            self.dict_line_pause_hour[day] = QLineEdit()
            self.dict_line_pause_hour[day].setText("1")
            self.dict_line_pause_hour[day].setFixedSize(50, 30)
            self.day_layout.addWidget(self.dict_line_pause_hour[day])
            self.label = QLabel("hour per day")
            self.day_layout.addWidget(self.label)
            self.dict_label_work_hour[day] = QLineEdit()
            self.dict_label_work_hour[day].setText("0:00")
            self.dict_label_work_hour[day].setFixedSize(50, 30)
            self.day_layout.addWidget(self.dict_label_work_hour[day])
            self.main_layout.addLayout(self.day_layout)

        self.main_layout.addWidget(QLabel("Total Work Hour"))
        self.total_work_hour_edit = QLineEdit()
        self.main_layout.addWidget(self.total_work_hour_edit)
        self.main_layout.addWidget(QLabel("Total Work Hour Per Day"))
        self.total_work_hour_per_day_edit = QLineEdit()
        self.main_layout.addWidget(self.total_work_hour_per_day_edit)

        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.calculate_work_hour)
        self.main_layout.addWidget(self.calculate_button)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_work_hour)
        self.main_layout.addWidget(self.save_button)

        self.load_button = QPushButton("Load")
        self.load_button.clicked.connect(self.load_work_hour)
        self.main_layout.addWidget(self.load_button)

        self.second_window = PopUpSaveJson()


    def calculate_work_hour(self):
        work_hour_list = []
        for day in self.weekdays:
            if self.dict_check_box[day].isChecked():
                hour_worked = substract_end_time_from_start_time(self.dict_line_edit_start[day].text(), self.dict_line_edit_end[day].text(), self.dict_line_pause_hour[day].text())
                self.dict_label_work_hour[day].setText(hour_worked)
                work_hour_list.append(hour_worked)

        self.total_work_hour_edit.setText(sum_hour_list(work_hour_list))

    def load_work_hour(self):
        load_work_hour_from_json_file()

    def save_work_hour(self):
        work_hour_dict = {}
        for day in self.weekdays:
            if self.dict_check_box[day].isChecked():
                work_hour_dict[day] = {"start": self.dict_line_edit_start[day].text(),
                                        "end": self.dict_line_edit_end[day].text(),
                                        "pause_hour": self.dict_line_pause_hour[day].text(),
                                        "hours worked": self.dict_label_work_hour[day].text()}

        # QDialog(self).setWindowTitle("Save Work Hour")
        # dialog = SaveWorkHourDialog(work_hour_dict)
        # dialog.exec_()
        # todo find a way to make this dialog appear
        self.second_window.work_hour_dict = work_hour_dict
        self.second_window.show()
        print("save success")


if '__main__' == __name__:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())