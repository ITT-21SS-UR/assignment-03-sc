import sys

from PyQt5 import QtGui, QtWidgets, QtCore

from trial_model import TrialModel, State

"""
EVENLY WORKLOAD DISTRIBUTION
3.1: Everyone did the task separately and Sarah combined the answers.
3.2: Was done together and text was written in Overleaf.
3.3: Discussing together and Claudia implemented the code.
3.4: Everyone conducted the tests evenly.
3.5: Discussing together and Sarah implemented the code.
3.6: Everyone did the task separately and Sarah combined the answers.
"""


class ReactionTimeTrial(QtWidgets.QWidget):

    @staticmethod
    def __draw_text(event, q_painter, description: str):
        q_painter.setPen(QtGui.QColor(20, 34, 100))
        q_painter.setFont(QtGui.QFont("Decorative", 18))
        q_painter.drawText(event.rect(), QtCore.Qt.AlignCenter, description)

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

    def __draw_circle(self, q_painter):
        if self.__trial_model.is_circle_shown():
            q_painter.setPen(QtGui.QColor(0, 0, 0))
            q_painter.setBrush(QtGui.QColor(119, 249, 158))  # mint green
            q_painter.drawEllipse(225, 125, 350, 350)

    def __draw_circle_with_number(self, event, q_painter):
        self.__draw_circle(q_painter)

        if self.__trial_model.is_circle_shown():
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
            description = "Please press 'space' when a circle with the number '" \
                          + str(self.__trial_model.get_correct_number()) \
                          + "' appears.\n" \
                            "Press 'space' to start."

            self.__draw_text(event, q_painter, description)

        elif trial_state == State.MENTAL_DEMAND:
            self.__draw_circle_with_number(event, q_painter)

        elif trial_state == State.DESCRIPTION_END:
            description = "You successfully completed the tasks.\n" \
                          "(≧∇≦)\n" \
                          "Thank you for your participation.\n" \
                          "To start a new study press 'space'."

            self.__draw_text(event, q_painter, description)

        q_painter.end()

    def keyPressEvent(self, event):
        self.__trial_model.key_pressed_event(event)


def get_input_participant_id():
    try:
        return int(sys.argv[1])
    except ValueError:
        print("invalid participant ID (-_-)")
        sys.exit()
    except IndexError:
        print("Please use the terminal and give a valid participant ID to start your program (-_-)")
        sys.exit()


def start_trial():
    participant_id = get_input_participant_id()

    app = QtWidgets.QApplication(sys.argv)
    trial = ReactionTimeTrial(participant_id)
    sys.exit(app.exec_())


if __name__ == '__main__':
    start_trial()
