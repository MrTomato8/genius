# -*- coding: utf-8 -*-
class OptionsCalculatorError(Exception):
    pass


class DuplicateCSV(OptionsCalculatorError):
    pass


class NotEnoughArguments(OptionsCalculatorError):
    pass


class PriceNotAvailable(Exception):
    pass

class TooLarge(Exception):
    pass

class TooSmall(Exception):
    pass

class TooLow(Exception):
    pass