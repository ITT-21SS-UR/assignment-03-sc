import random
from datetime import datetime
from enum import Enum

import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSignal


class State(Enum):
    START_COUNTDOWN = 1
    DESCRIPTION_SINGLE_STIMULUS = 2
    SINGLE_STIMULUS = 3
    DESCRIPTION_MENTAL_DEMAND = 4
    MENTAL_DEMAND = 5
    DESRIPTION_END = 6


class Condition(Enum):
    SINGLE_STIMULUS = "single stimulus"
    MENTAL_DEMAND = "mental demand"


class ShownStimulus(Enum):
    CIRCLE_APPEARS = "circle appears"
    CIRCLE_WITH_NUMBERS = "circle with numbers"


class TrialModel(QObject):
    # CSV column names
    PARTICIPANT_ID = "participant_id"
    CONDITION = "condition"
    SHOWN_STIMULUS = "shown_stimulus"
    PRESSED_KEY = "pressed_key"
    CORRECT_KEY = "is_correct_key"
    REACTION_TIME = "reaction_time_in_ms"
    TIMESTAMP = "timestamp"
    CIRCLE_APPEARED = "has_circle_appeared"
    CORRECT_REACTION = "is_correct_reaction"

    INVALID_TIME = "NaN"
    MAX_REPETITION_CONDITION = 2  # TODO after testing switch to 10

    data_changed = pyqtSignal()

    def __init__(self, participant_id):
        super().__init__()

        self.__participant_id = participant_id
        self.__is_circle = False
        self.__trial_counter = 0

        self.__state = State.DESCRIPTION_SINGLE_STIMULUS

        self.__condition = Condition.SINGLE_STIMULUS
        self.__shown_stimulus = ShownStimulus.CIRCLE_APPEARS.value
        self.__repetition_counter = 0

        self.__correct_number = self.get_random_number()
        self.__current_random_number = None

        self.__start_time = self.INVALID_TIME
        self.__end_time = self.INVALID_TIME

        self.__file = None
        self.__update_file()

    def __update_file(self):
        self.__file = "./log/id_" + str(self.__participant_id) \
                      + "_trial_" + str(self.__trial_counter) \
                      + ".csv"

    def get_correct_number(self):
        return self.__correct_number

    def get_repetion_counter(self):
        return self.__repetition_counter

    def __calculate_reaction_time(self):
        try:
            return (self.__end_time - self.__start_time).total_seconds() * 1000
            # TODO check if conversion to milliseconds is correct
        except AttributeError:  # TODO that's not pretty (a misused try except)
            return self.INVALID_TIME
        except TypeError:
            return self.INVALID_TIME

    def get_state(self):
        return self.__state

    def set_state(self, state):
        self.__state = state

    def get_trial_counter(self):
        return self.__trial_counter

    def increase_trial_counter(self):
        self.__trial_counter += 1
        self.__update_file()

    def get_participant_id(self):
        return self.__participant_id

    def is_circle_state(self):
        return self.__is_circle

    def __hide_circle(self):
        self.__start_time = self.INVALID_TIME
        self.__end_time = self.INVALID_TIME

        self.__is_circle = False
        self.data_changed.emit()

        self.start_countdown()

    def __show_circle(self):
        self.__is_circle = True
        self.__start_time = datetime.now()

        # TODO maybe generate new number here instead of view else it won't work?

        self.data_changed.emit()

        # TODO this is not working
        # if (self.__state == State.MENTAL_DEMAND) \
        #         and (self.__correct_number != self.__current_random_number):
        #     self.__current_random_number = self.get_random_number()  # TODO correct position for that
        #     timer = QtCore.QTimer(self)
        #     timer.start(2000)  # TODO how many milliseconds are good?
        #     timer.setSingleShot(True)
        #     timer.timeout.connect(self.__hide_circle)

    def get_condition(self):
        return self.__condition

    def get_random_number(self):
        random_number = random.randint(0, 3)
        self.__current_random_number = random_number
        #  TODO weighted numbers

        return random_number

    def start_countdown(self):
        self.__start_time = self.INVALID_TIME
        self.__end_time = self.INVALID_TIME

        self.__is_circle = False
        self.data_changed.emit()

        random_time = random.randint(3000, 6000)  # 3 - 6 sec between circle appearance

        timer = QtCore.QTimer(self)
        timer.start(random_time)
        timer.setSingleShot(True)
        timer.timeout.connect(self.__show_circle)

    @staticmethod
    def __is_space_key(key_code):
        if key_code == QtCore.Qt.Key_Space:
            return True

        return False

    def __is_correct_reaction(self, is_correct_key):
        if self.__is_circle and is_correct_key:
            if self.__state == State.MENTAL_DEMAND \
                    and (self.__current_random_number != self.__correct_number):
                return False

            return True

        return False

    def __create_row_data(self, key_code):
        is_correct_key = self.__is_space_key(key_code)

        return {
            self.PARTICIPANT_ID: self.__participant_id,
            self.CONDITION: self.__condition,
            self.SHOWN_STIMULUS: self.__shown_stimulus,
            self.PRESSED_KEY: key_code,
            self.CORRECT_KEY: is_correct_key,
            self.REACTION_TIME: self.__calculate_reaction_time(),
            self.TIMESTAMP: datetime.now(),
            self.CIRCLE_APPEARED: self.__is_circle,
            self.CORRECT_REACTION: self.__is_correct_reaction(is_correct_key)
        }

    def __handle_max_repetition(self):
        if self.__repetition_counter >= self.MAX_REPETITION_CONDITION:
            self.__repetition_counter = 0

            if self.__state == State.MENTAL_DEMAND:
                self.set_state(State.DESRIPTION_END)
            else:
                self.set_state(State.DESCRIPTION_MENTAL_DEMAND)
                self.__shown_stimulus = ShownStimulus.CIRCLE_WITH_NUMBERS.value

    def key_pressed_event(self, pressed_key):
        key_code = pressed_key.key()

        if self.__is_space_key(key_code):
            if self.__state == State.DESCRIPTION_SINGLE_STIMULUS:
                self.set_state(State.START_COUNTDOWN)
                self.start_countdown()

            elif self.__state == State.DESCRIPTION_MENTAL_DEMAND:
                self.__condition = Condition.MENTAL_DEMAND

                self.set_state(State.START_COUNTDOWN)
                self.start_countdown()

            elif self.__is_circle:
                self.__end_time = datetime.now()
                self.__write_to_csv(self.__create_row_data(key_code))  # order is important
                self.__hide_circle()

                self.__repetition_counter += 1
                # TODO only if a circle with the correct number appears increase repetition counter?
                self.__handle_max_repetition()

            elif self.__state == State.DESRIPTION_END:
                self.__reset_study()

            else:
                self.__write_to_csv(self.__create_row_data(key_code))

        else:
            self.__write_to_csv(self.__create_row_data(key_code))
            # log every user input even if it is not a relevant key
            # was done like this because of assignment description
            # to check if the pressed key is correct

    def __write_to_csv(self, row_data):
        try:
            data_frame = pd.read_csv(self.__file)
        except FileNotFoundError:  # TODO misused try except
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

    def __reset_study(self):  # TODO reset
        self.__participant_id += 1
        self.__is_circle = False
        self.__trial_counter = 0

        self.__state = State.DESCRIPTION_SINGLE_STIMULUS

        self.__condition = Condition.SINGLE_STIMULUS
        self.__shown_stimulus = ShownStimulus.CIRCLE_APPEARS.value
        self.__repetition_counter = 0

        self.__correct_number = self.get_random_number()
        self.__current_random_number = None

        self.__start_time = self.INVALID_TIME
        self.__end_time = self.INVALID_TIME

        self.__file = None
        self.__update_file()

        self.data_changed.emit()
