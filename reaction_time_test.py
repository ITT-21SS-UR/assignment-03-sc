#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys

from PyQt5 import QtWidgets


class ReactionTimeTest(QtWidgets.QWidget):
    """
    Measures the reaction time of a user when the circle changes the color to blue by pressing space.
    """

    def __init__(self, participant_id):
        super().__init__()
        self.__trial_counter = 0
        self.__participant_id = participant_id

        # TODO list with randomized condition setup


def get_input_participant_id():
    try:
        return int(sys.argv[1])
    except ValueError:
        print("invalid participant ID (-_-)")
        sys.exit()
    except IndexError:
        print("Please use the terminal and give a valid participant ID to start your program (-_-)")
        sys.exit()


def start_trials():
    MAX_TRIALS = 20
    participant_id = get_input_participant_id()

    app = QtWidgets.QApplication(sys.argv)
    # variable is never used, class automatically registers itself for Qt main loop:
    reactionTimeTest = ReactionTimeTest(participant_id)
    sys.exit(app.exec_())


if __name__ == '__main__':
    start_trials()
