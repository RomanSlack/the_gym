"""Hammer Strength Select Hip Adduction, Charcoal frame / Black upholstery, the arms open at the start.

The abduction's sister (same frame, tower, seat and arms; refs/ ref_01 the maker's studio three-quarter, the used pair's
photos in the abduction's refs/): built by the abduction's model.py with ADDUCTION = True: the knee pads inside the
knees, the arms opened 25 degrees at the start; to Life Fitness's 61 x 26 x 55 in.
"""
import importlib.util
import math
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "abduction", Path(__file__).resolve().parent.parent / "hammer-strength-select-hip-abduction" / "model.py")
abd = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(abd)
abd.ADDUCTION = True
abd.OPEN = math.radians(25)

LOOK, VIEWS, DETAILS = abd.LOOK, abd.VIEWS, abd.DETAILS


def build(k):
    abd.build(k)
