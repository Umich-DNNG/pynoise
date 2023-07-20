# standard imports
import unittest

# third party imports

# local imports
from lmx.Event import Event


class TestEvent(unittest.TestCase):
    """unit test for the Event class."""

    def test_constructors(self):
        myEvent = Event(detector=7, time=54)
        self.assertEqual(myEvent.detector, 7)
        self.assertEqual(myEvent.time, 54)

    def test_failures(self):
        # there is a negative detector number:
        with self.assertRaises(ValueError):
            event = Event(detector=-1, time=54)

        # there is a negative time detector:
        with self.assertRaises(ValueError):
            event = Event(detector=1, time=-54)

    def test_comparison(self):
        reference = Event(detector=1, time=1800)
        equal = Event(detector=1, time=1800)
        different = Event(detector=2, time=12)

        self.assertTrue(reference == equal)
        self.assertFalse(reference == different)
        self.assertFalse(reference != equal)
        self.assertTrue(reference != different)


if __name__ == '__main__':
    unittest.main()
