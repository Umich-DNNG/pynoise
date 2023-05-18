# standard imports
import unittest
import sys
sys.path.append(r"C:\Users\352798\python")
# local imports
from lmx.rossi.RossiHistogram import RossiHistogram


class TestRossiHistogram(unittest.TestCase):
    """Unit test for the RossiHistogram class."""

    frequency = [1]
    reset_time = 2.

    def test_constructors(self):
        histogram = RossiHistogram(reset_time=self.reset_time,
                                   frequency=self.frequency)

        self.assertEqual(histogram.reset_time, 2.)
        self.assertEqual(histogram.number_bins, 1)
        self.assertEqual(len(histogram.frequency), 1)
        self.assertEqual(histogram.frequency[0], 1)
        self.assertEqual(histogram.frequency[-1], 1)
        self.assertEqual(histogram.bins[0], 1)
        self.assertEqual(histogram.bins[-1], 1.)
        self.assertEqual(len(histogram.bins), 1)

    def test_methods(self):
        pass
        # Only method (plotHistogram) does not alter class

    def test_construction_failures(self):
        # None value reset_time
        with self.assertRaises(ValueError):
            histogram = RossiHistogram(reset_time=None, frequency=self.frequency)

        # 0 value reset_time
        with self.assertRaises(ValueError):
            histogram = RossiHistogram(reset_time=0., frequency=self.frequency)

        # negative value reset_time
        with self.assertRaises(ValueError):
            histogram = RossiHistogram(reset_time=-1., frequency=self.frequency)

        # non-float value instead of numerical reset_time
        with self.assertRaises(ValueError):
            histogram = RossiHistogram(reset_time="", frequency=self.frequency)

        # None value frequency
        with self.assertRaises(ValueError):
            histogram = RossiHistogram(reset_time=self.reset_time, frequency=None)

        # empty frequency
        with self.assertRaises(ValueError):
            histogram = RossiHistogram(reset_time=self.reset_time, frequency=[])

        # non-list value as frequency
        with self.assertRaises(ValueError):
            histogram = RossiHistogram(reset_time=self.reset_time, frequency=1)

    def test_setter_failures(self):
        histogram = RossiHistogram(reset_time=self.reset_time, frequency=self.frequency)
        # None value reset_time
        with self.assertRaises(ValueError):
            histogram.reset_time = None

        # 0 value reset_time
        with self.assertRaises(ValueError):
            histogram.reset_time = 0.

        # negative value reset_time
        with self.assertRaises(ValueError):
            histogram.reset_time = -1.

        # str value instead of float reset_time
        with self.assertRaises(ValueError):
            histogram.reset_time = "a"

        # None value frequency
        with self.assertRaises(ValueError):
            histogram.frequency = None

        # empty frequency
        with self.assertRaises(ValueError):
            histogram.frequency = []

        # int value as frequency
        with self.assertRaises(ValueError):
            histogram.frequency = 1

        # None value bins
        with self.assertRaises(ValueError):
            histogram.bins = None

        # empty list
        with self.assertRaises(ValueError):
            histogram.bins = []

        # int value as bins
        with self.assertRaises(ValueError):
            histogram.bins = 1

        # None as length of bins
        with self.assertRaises(ValueError):
            histogram.number_bins = None

        # Float as length of bins
        with self.assertRaises(ValueError):
            histogram.number_bins = 1.


if __name__ == '__main__':
    unittest.main()
