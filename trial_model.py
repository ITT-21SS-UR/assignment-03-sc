from datetime import datetime

import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSignal


class TrialModel(QObject):
    PARTICIPANT_ID = "participant_id"
    CONDITION = "condition"
    SHOWN_STIMULUS = "shown_stimulus"
    PRESSED_KEY = "pressed_key"
    CORRECT_KEY = "correct_key"
    REACTION_TIME = "reaction_time"
    TIMESTAMP = "timestamp"
    CIRCLE_APPEARED = "circle_appeared"
    CORRECT_REACTION = "correct_reaction"

    data_changed = pyqtSignal()

    def __init__(self, participant_id):
        super().__init__()

        self.__participant_id = participant_id
        self.__is_circle = False
        self.__trial_counter = 0  # TODO

        self.__condition = 1  # TODO
        self.__test_counter = 0  # TODO

        self.__start_time = -1
        self.__end_time = -1

        self.__file = "./log/id_" + str(self.__participant_id) \
                      + "_trial_" + str(self.__trial_counter) \
                      + ".csv"

    def __calculate_reaction_time(self):
        try:
            return (self.__end_time - self.__start_time).total_seconds() * 1000
            # TODO check if conversion to milliseconds is correct
        except AttributeError:  # that's not pretty (a misused try except)
            return -1

    def get_circle_state(self):
        return self.__is_circle

    def change_circle_state(self):
        if self.__is_circle:
            self.__is_circle = False
            # maybe start the countdown here when it is not shown
            # TODO maybe create separate custom signal
        else:
            self.__is_circle = True
            # self.__start_time = datetime.now()  # TODO maybe at another/better place

        self.data_changed.emit()

    def get_trial_counter(self):
        return self.__trial_counter

    def increase_trial_counter(self):
        self.__trial_counter += 1

    def get_participant_id(self):
        return self.__participant_id

    def start_countdown(self):
        # TODO after timer is ended
        # TODO asynchronous
        self.__start_time = -1
        self.__end_time = -1

        self.__is_circle = False
        self.data_changed.emit()
        # self.change_circle_state()
        # TODO randomize countdown
        # after countdown is 0 self.__start_time = datetime.now() # reset start_time
        # and self.data_changed.emit() again

    @staticmethod
    def __is_correct_key(key_code):
        if key_code == QtCore.Qt.Key_Space:
            return True

        return False

    def __is_correct_reaction(self, is_correct_key):
        if self.__is_circle and is_correct_key:
            return True

        return False

    def __create_row_data(self, key_code):
        is_correct_key = self.__is_correct_key(key_code)

        return {
            self.PARTICIPANT_ID: self.__participant_id,
            self.CONDITION: self.__condition,  # TODO condition Boolean mit oder ohne Bilder
            self.SHOWN_STIMULUS: "circle appears",  # is always the same for this assignment
            self.PRESSED_KEY: key_code,
            self.CORRECT_KEY: is_correct_key,
            self.REACTION_TIME: self.__calculate_reaction_time(),
            self.TIMESTAMP: datetime.now(),
            self.CIRCLE_APPEARED: self.__is_circle,
            self.CORRECT_REACTION: self.__is_correct_reaction(is_correct_key)
        }

    def key_pressed_event(self, pressed_key):
        # TODO check for the first time if the space was typed to start the trial
        key_code = pressed_key.key()
        row_data = self.__create_row_data(key_code)
        if self.__is_correct_key(key_code):
            # TODO check if circle is shown if yes log that it is a valid input
            # and hide circle from view
            # only if the circle is displayed

            # self.__trial_model.increase_trial_counter()
            if self.__is_circle:
                self.__end_time = datetime.now()
                self.__write_to_csv(row_data)
                self.change_circle_state()
                #  TODO start_countdown
            else:
                self.start_countdown()  # TODO condition because it should not start directly; at this place only for testing
                self.__write_to_csv(row_data)
                # TODO do nothing just resume countdown
            # change circle state only if it is valid to be changed
        else:
            self.__write_to_csv(row_data)

    def __write_to_csv(self, row_data):
        try:
            data_frame = pd.read_csv(self.__file)
        except FileNotFoundError:
            data_frame = pd.DataFrame(columns=[
                self.PARTICIPANT_ID,
                self.CONDITION,
                self.SHOWN_STIMULUS,
                self.PRESSED_KEY,
                self.CORRECT_KEY,
                self.REACTION_TIME,
                self.TIMESTAMP,
                self.CIRCLE_APPEARED,
                self.CORRECT_REACTION
            ])

        data_frame = data_frame.append(row_data, ignore_index=True)
        data_frame.to_csv(self.__file, index=False)
