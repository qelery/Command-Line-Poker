import re
from unittest import TestCase


class PokerTestCase(TestCase):
    def assertEqualStripColor(self, a: str, b: str):
        """Fail if the two strings are unequal, regardless of color sequences."""
        self.assertEqual(_strip_color(a), _strip_color(b))


def _strip_color(s: str):
    """Strips the color-coding sequences from a string"""
    s = re.sub(r'\x1b\[([0-9,A-Z]{1,2}(;[0-9]{1,2})?(;[0-9]{3})?)?[m|K]?', '', s)
    return re.sub(r'\x1b\(B', '', s)
