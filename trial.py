import sys

from PyQt5 import QtGui, QtWidgets, QtCore

from trial_model import TrialModel


class Trial(QtWidgets.QWidget):
    def __init__(self, participant_id):
        super().__init__()

        self.__trial_model = TrialModel(participant_id)
        self.__setup_ui()

    def __setup_ui(self):
        self.setGeometry(550, 200, 800, 600)
        self.setWindowTitle("Trial - Circle Space Clicker")
        self.setStyleSheet("background: rgb(202, 237, 224);")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.__trial_model.data_changed.connect(self.__data_changed)

        self.show()

    def __data_changed(self):
        self.update()

    @staticmethod
    def __draw_text(event, q_painter):
        text = "Please press 'space' when the circle appears."
        q_painter.setPen(QtGui.QColor(20, 34, 100))
        q_painter.setFont(QtGui.QFont("Decorative", 18))
        q_painter.drawText(event.rect(), QtCore.Qt.AlignHCenter, text)

    def __draw_circle(self, q_painter):
        # TODO depending on condition
        if self.__trial_model.get_circle_state():
            q_painter.setPen(QtGui.QColor(0, 0, 0))
            q_painter.setBrush(QtGui.QColor(119, 249, 158))  # mint green
            q_painter.drawEllipse(225, 100, 350, 350)

        else:  # TODO start the countdown so that the circle can be shown at a later time
            self.__trial_model.start_countdown()

    def paintEvent(self, event):
        q_painter = QtGui.QPainter()
        q_painter.begin(self)
        self.__draw_text(event, q_painter)
        self.__draw_circle(q_painter)
        q_painter.end()

    def keyPressEvent(self, event):
        self.__trial_model.key_pressed_event(event)


if __name__ == '__main__':
    # from datetime import datetime
    # __start_time = datetime.now()
    # test_time = datetime.now()
    # print((__start_time - test_time).total_seconds() * 1000)

    app = QtWidgets.QApplication(sys.argv)
    trial = Trial(100)
    sys.exit(app.exec_())
