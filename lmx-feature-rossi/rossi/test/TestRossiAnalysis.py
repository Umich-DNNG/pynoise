# standard imports
import unittest

# local imports
from lmx.rossi.RossiHistogram import RossiHistogram
from lmx.rossi.RossiHistogramAnalysis import RossiHistogramAnalysis


class TestRossiAnalysis(unittest.TestCase):
    """Unit test for the RossiHistogramAnalysis class."""

    frequency = [1]
    reset_time = 2.
    histogram_ = RossiHistogram(reset_time=reset_time, frequency=frequency)

    def test_constructors(self):
        analysis = RossiHistogramAnalysis(histogram=self.histogram_)

        self.assertEqual(analysis.histogram.reset_time, 2.)
        self.assertEqual(analysis.histogram.number_bins, 1)
        self.assertEqual(len(analysis.histogram.frequency), 1)
        self.assertEqual(analysis.histogram.frequency[0], 1)
        self.assertEqual(analysis.histogram.frequency[-1], 1)
        self.assertEqual(analysis.histogram.bins[0], 1)
        self.assertEqual(analysis.histogram.bins[-1], 1.)
        self.assertEqual(len(analysis.histogram.bins), 1)

    def test_failures(self):
        with self.assertRaises(ValueError):
            analysis = RossiHistogramAnalysis(histogram=[])
        with self.assertRaises(ValueError):
            analysis = RossiHistogramAnalysis(histogram=1)
        with self.assertRaises(ValueError):
            analysis = RossiHistogramAnalysis(histogram=self.histogram_)
            analysis.histogram = None
        with self.assertRaises(ValueError):
            analysis = RossiHistogramAnalysis(histogram=self.histogram_)
            analysis.histogram = []
        with self.assertRaises(ValueError):
            analysis = RossiHistogramAnalysis(histogram=self.histogram_)
            analysis.histogram = 1


if __name__ == '__main__':
    unittest.main()
