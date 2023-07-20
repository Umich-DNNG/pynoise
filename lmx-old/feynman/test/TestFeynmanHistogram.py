# standard imports
import unittest

# import sys
# sys.path.append(r"C:\Users\352798\python")

# local imports
from lmx.feynman.FeynmanHistogram import FeynmanHistogram


class TestFeynmanHistogram(unittest.TestCase):
    """Unit test for the FeynmanHistogram class."""

    frequency = [1]
    gatewidth = 2.

    def test_constructors(self):
        histogram = FeynmanHistogram(gatewidth=self.gatewidth,
                                     frequency=self.frequency)

        self.assertEqual(histogram.gatewidth, 2.)
        self.assertEqual(histogram.number_gates, 1)
        self.assertEqual(len(histogram.frequency), 1)
        self.assertEqual(histogram.frequency[0], 1)
        self.assertEqual(histogram.frequency[-1], 1)
        self.assertEqual(len(histogram.normalised_frequency), 1)
        self.assertEqual(histogram.normalised_frequency[0], 1)
        self.assertEqual(histogram.normalised_frequency[-1], 1)

    def test_methods(self):
        histogram = FeynmanHistogram(gatewidth=self.gatewidth,
                                     frequency=[1, 2, 3, 4])

        self.assertAlmostEqual(histogram.reduced_factorial_moment(1), 2.)
        self.assertAlmostEqual(histogram.reduced_factorial_moment(2), 1.5)
        self.assertAlmostEqual(histogram.reduced_factorial_moment(3), 0.4)
        self.assertAlmostEqual(histogram.reduced_factorial_moment(4), 0.)

        self.assertAlmostEqual(histogram.factorial_moment(1), 2.)
        self.assertAlmostEqual(histogram.factorial_moment(2), 5.)
        self.assertAlmostEqual(histogram.factorial_moment(3), 13.4)
        self.assertAlmostEqual(histogram.factorial_moment(4), 37.4)

        self.assertAlmostEqual(histogram.mean, 2.)
        self.assertAlmostEqual(histogram.variance, 5.)
        self.assertAlmostEqual(histogram.variance_to_mean, -0.5)

        self.assertAlmostEqual(histogram.Y1[0], 1000000000., places=5)
        self.assertAlmostEqual(histogram.Y1[1], 166666666.6666666, places=5)
        self.assertAlmostEqual(histogram.Y2[0], -250000000.0000000, places=5)
        self.assertAlmostEqual(histogram.Y2[1], 214087209.64441875, places=5)

        self.assertAlmostEqual(histogram.R1(1.), 1000000000., places=5)
        self.assertAlmostEqual(histogram.R2(1.), -440398538.98894215, places=5)

    def test_construction_failures(self):
        # None gatewidth at construction
        with self.assertRaises(ValueError):
            histogram = FeynmanHistogram(gatewidth=None, frequency=self.frequency)

        # Zero value gatewidth at construction
        with self.assertRaises(ValueError):
            histogram = FeynmanHistogram(gatewidth=0., frequency=self.frequency)

        # Negative gatewidth at construction
        with self.assertRaises(ValueError):
            histogram = FeynmanHistogram(gatewidth=-1., frequency=self.frequency)

        # Non-float gatewidth at construction
        with self.assertRaises(ValueError):
            histogram = FeynmanHistogram(gatewidth="1", frequency=self.frequency)

        # None frequency at construction
        with self.assertRaises(ValueError):
            histogram = FeynmanHistogram(gatewidth=self.gatewidth, frequency=None)

        # Empty frequency at construction
        with self.assertRaises(ValueError):
            histogram = FeynmanHistogram(gatewidth=self.gatewidth, frequency=[])

        # Non-list frequency at construction
        with self.assertRaises(ValueError):
            histogram = FeynmanHistogram(gatewidth=self.gatewidth, frequency=1)

    def test_setter_failures(self):
        histogram = FeynmanHistogram(gatewidth=self.gatewidth, frequency=self.frequency)

        # None gatewidth
        with self.assertRaises(ValueError):
            histogram.gatewidth = None

        # Zero value gatewidth
        with self.assertRaises(ValueError):
            histogram.gatewidth = 0.

        # Negative gatewidth
        with self.assertRaises(ValueError):
            histogram.gatewidth = -1.

        # Non-float gatewidth
        with self.assertRaises(ValueError):
            histogram.gatewidth = "1"

        # None frequency
        with self.assertRaises(ValueError):
            histogram.frequency = None

        # empty frequency
        with self.assertRaises(ValueError):
            histogram.frequency = []

        # Non-list frequency
        with self.assertRaises(ValueError):
            histogram.frequency = 1

        # None number of gates
        with self.assertRaises(ValueError):
            histogram.number_gates = None

        # Zero value number of gates
        with self.assertRaises(ValueError):
            histogram.number_gates = 0

        # Negative number of gates
        with self.assertRaises(ValueError):
            histogram.number_gates = -1

        # Non-int number of gates
        with self.assertRaises(ValueError):
            histogram.number_gates = 1.

        # None normalized frequency
        with self.assertRaises(ValueError):
            histogram.normalised_frequency = None

        # empty normalized frequency
        with self.assertRaises(ValueError):
            histogram.normalised_frequency = []

        # Non-list normalized frequency
        with self.assertRaises(ValueError):
            histogram.normalised_frequency = 1

    def test_method_failures(self):
        # not implemented reduced factorial moment
        with self.assertRaises(NotImplementedError):
            histogram = FeynmanHistogram(gatewidth=self.gatewidth, frequency=self.frequency)

            moment = histogram.reduced_factorial_moment(0)

        with self.assertRaises(NotImplementedError):
            histogram = FeynmanHistogram(gatewidth=self.gatewidth, frequency=self.frequency)

            moment = histogram.reduced_factorial_moment(None)

        # None value factorial moment
        with self.assertRaises(ValueError):
            histogram = FeynmanHistogram(gatewidth=self.gatewidth, frequency=self.frequency)

            moment = histogram.factorial_moment(None)

        # None value R1
        with self.assertRaises(ValueError):
            histogram = FeynmanHistogram(gatewidth=self.gatewidth, frequency=self.frequency)

            R1 = histogram.R1(None)

        # Non-numerical value R1
        with self.assertRaises(ValueError):
            histogram = FeynmanHistogram(gatewidth=self.gatewidth, frequency=self.frequency)

            R1 = histogram.R1("a")

        # None value R2
        with self.assertRaises(ValueError):
            histogram = FeynmanHistogram(gatewidth=self.gatewidth, frequency=self.frequency)

            R2 = histogram.R2(None)

        # Non-numerical value R2
        with self.assertRaises(ValueError):
            histogram = FeynmanHistogram(gatewidth=self.gatewidth, frequency=self.frequency)

            R2 = histogram.R2("a")


if __name__ == '__main__':
    unittest.main()
