from typing import List
import pickle

# local imports
from lmx.feynman.FeynmanHistogram import FeynmanHistogram


def pickleFeynman(data: FeynmanHistogram or List[FeynmanHistogram], file: str):
    """Save Feynman data through python pickling

        Arguments:
            data: FeynmanHistogram type(s)
            file: name of file to be save to
    """
    if file.endswith(".npy") is False:
        file = file + ".npy"

    with open(file, "wb") as out_file:
        pickle.dump(data, out_file)


def unpickleFeynman(file):
    """Load Feynman data though python unpickling

        Arguments:
            file: name of data file

        Returns: A singular or list of FeynmanHistogram Class variables
    """
    if file.endswith(".npy") is False:
        file = file + ".npy"

    with open(file, "rb") as in_file:
        return pickle.load(in_file)
