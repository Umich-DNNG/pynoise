from typing import List
import pickle

# local imports
from lmx.rossi.RossiHistogram import RossiHistogram


def pickleRossi(data: RossiHistogram or List[RossiHistogram], file: str):
    """Save Rossi data through python pickling

        Arguments:
            data: RossiHistogram type(s)
            file: name of file to be save to
    """
    if file.endswith(".npy") is False:
        file = file + ".npy"

    with open(file, "wb") as out_file:
        pickle.dump(data, out_file)


def unpickleRossi(file):
    """Load Rossi data though python unpickling

        Arguments:
            file: name of data file

        Returns: A singular or list of RossiHistogram type variables
    """
    if file.endswith(".npy") is False:
        file = file + ".npy"

    with open(file, "rb") as in_file:
        return pickle.load(in_file)
