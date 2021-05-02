import sys

from PyQt5 import QtGui, QtWidgets, QtCore

from trial_model import TrialModel, State, Condition


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
    def __draw_text(event, q_painter, description: str):
        q_painter.setPen(QtGui.QColor(20, 34, 100))
        q_painter.setFont(QtGui.QFont("Decorative", 18))
        q_painter.drawText(event.rect(), QtCore.Qt.AlignCenter, description)

    def __draw_circle(self, q_painter):
        if self.__trial_model.is_circle_state():
            q_painter.setPen(QtGui.QColor(0, 0, 0))
            q_painter.setBrush(QtGui.QColor(119, 249, 158))  # mint green
            q_painter.drawEllipse(225, 125, 350, 350)

    def __draw_circle_with_number(self, event, q_painter):
        self.__draw_circle(q_painter)

        if self.__trial_model.is_circle_state():
            q_painter.setPen(QtGui.QColor(0, 0, 0))  # black
            q_painter.setFont(QtGui.QFont("Decorative", 150))

            number = self.__trial_model.get_random_number()
            q_painter.drawText(event.rect(), QtCore.Qt.AlignCenter, str(number))

    def paintEvent(self, event):
        q_painter = QtGui.QPainter()
        q_painter.begin(self)

        trial_state = self.__trial_model.get_state()
        if trial_state == State.DESCRIPTION_SINGLE_STIMULUS:
            description = "Please press 'space' when a circle appears.\n" \
                          "Press 'space' to start."

            self.__draw_text(event, q_painter, description)

        elif trial_state == State.SINGLE_STIMULUS:
            self.__draw_circle(q_painter)

        elif trial_state == State.DESCRIPTION_MENTAL_DEMAND:
            description = "Please press 'space' when a circle with the number " \
                          + str(self.__trial_model.get_correct_number()) \
                          + " appears.\n" \
                            "If a circle with another number appears just ignore it.\n" \
                            "It will disappear from alone.\n" \
                            "Press 'space' to start."

            self.__draw_text(event, q_painter, description)

        elif trial_state == State.MENTAL_DEMAND:
            self.__draw_circle_with_number(event, q_painter)

        elif trial_state == State.DESRIPTION_END:
            description = "You successfully completed the tasks.\n" \
                          "(≧∇≦)\n" \
                          "Thank you for your participation.\n" \
                          "To start a new study press 'space'"

            self.__draw_text(event, q_painter, description)

        q_painter.end()

    def keyPressEvent(self, event):
        self.__trial_model.key_pressed_event(event)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    trial = Trial(100)
    sys.exit(app.exec_())
