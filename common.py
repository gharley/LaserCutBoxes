from enum import Enum
import numpy as np


# DotDict - easy dictionary access
class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


# Box type enums
class BoxType(Enum):
    All = 0
    SLOTS = 1
    TABS = 2


# Helper methods
def get_vectors(width, height):
    lower_left = vector(0, -height)
    upper_left = vector(0, 0)
    lower_right = vector(width, -height)
    upper_right = vector(width, 0)

    return lower_left, upper_left, lower_right, upper_right


def vector(x, y):
    return np.array([float(x), float(y)])
