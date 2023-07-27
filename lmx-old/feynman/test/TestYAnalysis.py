# standard imports
import unittest

# local imports
from lmx.feynman.FeynmanHistogram import FeynmanHistogram
from lmx.feynman.FeynmanYAnalysis import FeynmanYAnalysis


class TestRossiAnalysis(unittest.TestCase):
    """Unit test for the RossiHistogramAnalysis class."""

    frequency = [1]
    gatewidth = 2.
    histogram = FeynmanHistogram(gatewidth=gatewidth, frequency=frequency)

    def test_constructors(self):
        analysis = FeynmanYAnalysis(histograms=[self.histogram])

        self.assertEqual(analysis.histograms[0].gatewidth, 2.)
        self.assertEqual(analysis.histograms[0].number_gates, 1)
        self.assertEqual(len(analysis.histograms[0].frequency), 1)
        self.assertEqual(analysis.histograms[0].frequency[0], 1)
        self.assertEqual(analysis.histograms[0].frequency[-1], 1)
        self.assertEqual(len(analysis.histograms[0].normalised_frequency), 1)
        self.assertEqual(analysis.histograms[0].normalised_frequency[0], 1)
        self.assertEqual(analysis.histograms[0].normalised_frequency[-1], 1)

    def test_failures(self):
        with self.assertRaises(ValueError):
            analysis = FeynmanYAnalysis(histograms=[])
        with self.assertRaises(ValueError):
            analysis = FeynmanYAnalysis(histograms=1)
        with self.assertRaises(ValueError):
            analysis = FeynmanYAnalysis(histograms=[self.histogram])
            analysis.histograms = None
        with self.assertRaises(ValueError):
            analysis = FeynmanYAnalysis(histograms=[self.histogram])
            analysis.histograms = []
        with self.assertRaises(ValueError):
            analysis = FeynmanYAnalysis(histograms=[self.histogram])
            analysis.histograms = 1


if __name__ == '__main__':
    unittest.main()
