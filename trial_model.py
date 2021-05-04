import os
import random
from datetime import datetime
from enum import Enum

import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSignal


class State(Enum):
    INIT_CIRCLE = 1
    DESCRIPTION_SINGLE_STIMULUS = 2
    SINGLE_STIMULUS = 3
    DESCRIPTION_MENTAL_DEMAND = 4
    MENTAL_DEMAND = 5
    DESCRIPTION_END = 6


class Condition(Enum):
    SINGLE_STIMULUS = "single stimulus"
    MENTAL_DEMAND = "mental demand"


class ShownStimulus(Enum):
    CIRCLE_APPEARS = "circle appears"
    CIRCLE_WITH_NUMBERS = "circle with number"


class TrialModel(QObject):
    # CSV column names
    PARTICIPANT_ID = "participant_id"
    CONDITION = "condition"
    SHOWN_STIMULUS = "shown_stimulus"
    PRESSED_KEY = "pressed_key"
    CORRECT_KEY = "is_correct_key"
    REACTION_TIME = "reaction_time_in_ms"
    TIMESTAMP = "timestamp"
    CIRCLE_APPEARED = "is_circle_shown"
    CIRCLE_COUNTER = "number_of_circles"
    CORRECT_NUMBER = "is_correct_number"
    CORRECT_REACTION = "is_correct_reaction"

    INVALID_TIME = "NaN"
    MAX_REPETITION_CONDITION = 10

    data_changed = pyqtSignal()

    @staticmethod
    def __is_space_key(key_code):
        return key_code == QtCore.Qt.Key_Space

    @staticmethod
    def __generate_random_number():
        return random.randint(1, 3)

    def __init__(self, participant_id):
        super().__init__()

        self.__create_log_directory()
        self.__reset_model(participant_id)

    def __create_log_directory(self):
        self.__log_directory = "log"

        if not os.path.isdir(self.__log_directory):
            os.makedirs(self.__log_directory)

    def __reset_model(self, participant_id):
        self.__participant_id = participant_id

        self.__is_circle = False
        self.__state = State.DESCRIPTION_SINGLE_STIMULUS

        self.__set_condition(Condition.SINGLE_STIMULUS)
        self.__shown_stimulus = ShownStimulus.CIRCLE_APPEARS
        self.__repetition_counter = 0
        self.__circle_counter = 0

        self.__correct_number = self.__generate_random_number()
        self.__current_random_number = 0

        self.__start_time = self.INVALID_TIME
        self.__end_time = self.INVALID_TIME

        self.__timer = QtCore.QTimer(self)
        self.__timer.timeout.connect(self.__on_timeout)

    def __set_random_number(self):
        self.__current_random_number = self.__generate_random_number()

    def __set_condition(self, condition):
        self.__condition = condition
        self.__update_file()

    def __update_file(self):
        self.__file = "./" + self.__log_directory + "/id_" + str(self.__participant_id) \
                      + "_trial_" + self.__condition.value \
                      + ".csv"

    def __on_timeout(self):
        if self.__state == State.SINGLE_STIMULUS \
                or self.__state == State.MENTAL_DEMAND:

            if self.__is_circle:
                self.__hide_circle()
            else:
                self.__show_circle()

    def __hide_circle(self):
        if not self.__is_circle:
            return

        self.__is_circle = False
        self.data_changed.emit()

        self.__start_countdown()

    def __show_circle(self):
        self.__circle_counter += 1

        self.__is_circle = True
        self.__start_time = datetime.now()

        if self.__state == State.MENTAL_DEMAND:
            self.__set_random_number()

        self.data_changed.emit()

        if self.__state == State.MENTAL_DEMAND \
                and self.__correct_number != self.__current_random_number:
            self.__timer.setSingleShot(True)
            self.__timer.start(2000)

    def __start_countdown(self):
        self.__start_time = self.INVALID_TIME
        self.__end_time = self.INVALID_TIME
        self.__is_circle = False

        if self.__state == State.INIT_CIRCLE:
            if self.__condition == Condition.SINGLE_STIMULUS:
                self.__state = State.SINGLE_STIMULUS

            elif self.__condition == Condition.MENTAL_DEMAND:
                self.__state = State.MENTAL_DEMAND

        self.data_changed.emit()

        self.__timer.setSingleShot(True)
        # 2 - 5 sec between circle appearance
        self.__timer.start(random.randint(2000, 5000))

    def __is_correct_number(self):
        if self.__state == State.MENTAL_DEMAND \
                and self.__correct_number == self.__current_random_number:
            return True

        elif self.__state == State.SINGLE_STIMULUS:
            return ""

        return False

    def __is_correct_reaction(self, is_correct_key):
        if self.__is_circle and is_correct_key:
            if self.__state == State.MENTAL_DEMAND \
                    and self.__current_random_number != self.__correct_number:
                return False

            return True

        return False

    def __handle_repetition_counter(self):
        if self.__state == State.SINGLE_STIMULUS:
            self.__repetition_counter += 1

        elif self.__state == State.MENTAL_DEMAND \
                and self.__correct_number == self.__current_random_number:
            self.__repetition_counter += 1

        self.__handle_max_repetition()

    def __handle_max_repetition(self):
        if self.__repetition_counter >= self.MAX_REPETITION_CONDITION:
            self.__repetition_counter = 0

            if self.__state == State.MENTAL_DEMAND:
                self.__state = State.DESCRIPTION_END
            else:
                self.__state = State.DESCRIPTION_MENTAL_DEMAND
                self.__shown_stimulus = ShownStimulus.CIRCLE_WITH_NUMBERS

    def __reset_study(self):
        self.__reset_model(self.__participant_id + 1)
        self.data_changed.emit()

    def __calculate_reaction_time(self):
        try:
            return (self.__end_time - self.__start_time).total_seconds() * 1000
        except AttributeError:
            return self.INVALID_TIME
        except TypeError:
            return self.INVALID_TIME

    def __create_shown_stimulus_entry(self):
        shown_stimulus_value = self.__shown_stimulus.value
        if self.__state == State.MENTAL_DEMAND:
            return shown_stimulus_value + " " + str(self.__current_random_number)

        return shown_stimulus_value

    def __create_row_data(self, key_code):
        is_correct_key = self.__is_space_key(key_code)

        return {
            self.PARTICIPANT_ID: self.__participant_id,
            self.CONDITION: self.__condition.value,
            self.SHOWN_STIMULUS: self.__create_shown_stimulus_entry(),
            self.PRESSED_KEY: key_code,
            self.CORRECT_KEY: is_correct_key,
            self.REACTION_TIME: self.__calculate_reaction_time(),
            self.TIMESTAMP: datetime.now(),
            self.CIRCLE_APPEARED: self.__is_circle,
            self.CIRCLE_COUNTER: self.__circle_counter,
            self.CORRECT_NUMBER: self.__is_correct_number(),
            self.CORRECT_REACTION: self.__is_correct_reaction(is_correct_key),
        }

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
                self.CIRCLE_COUNTER,
                self.CORRECT_NUMBER,
                self.CORRECT_REACTION
            ])

        data_frame = data_frame.append(row_data, ignore_index=True)
        data_frame.to_csv(self.__file, index=False)

    def get_state(self):
        return self.__state

    def get_correct_number(self):
        return self.__correct_number

    def get_random_number(self):
        return self.__current_random_number

    def is_circle_shown(self):
        return self.__is_circle

    def key_pressed_event(self, pressed_key):
        key_code = pressed_key.key()

        if self.__is_space_key(key_code):
            if self.__state == State.DESCRIPTION_SINGLE_STIMULUS:
                self.__state = State.INIT_CIRCLE
                self.__start_countdown()

            elif self.__state == State.DESCRIPTION_MENTAL_DEMAND:
                self.__set_condition(Condition.MENTAL_DEMAND)
                self.__state = State.INIT_CIRCLE
                self.__start_countdown()

            elif self.__is_circle:
                self.__end_time = datetime.now()
                self.__write_to_csv(self.__create_row_data(key_code))  # order is important
                self.__hide_circle()

                self.__handle_repetition_counter()

            elif self.__state == State.DESCRIPTION_END:
                self.__reset_study()

            else:
                self.__write_to_csv(self.__create_row_data(key_code))

        elif self.__state == State.SINGLE_STIMULUS \
                or self.__state == State.MENTAL_DEMAND:
            self.__write_to_csv(self.__create_row_data(key_code))
            # log every user input in these states even if it is not a relevant key
            # was done like this because of assignment description
            # to check if the pressed key is correct
