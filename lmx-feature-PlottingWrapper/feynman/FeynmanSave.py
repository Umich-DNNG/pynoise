from marshmallow import Schema, fields, post_load, ValidationError
from lmx.feynman.FeynmanHistogram import FeynmanHistogram
import json
import pickle


def PickleRossi(data, file):
    with open(file, "wb") as out_file:
        pickle.dump(data, out_file)


def UnpickleRossi(file):
    with open(file, "rb") as in_file:
        FeynmanHist = pickle.load(in_file)
        return FeynmanHist


class FeynmanSchema(Schema):
    gatewidth = fields.Float(required=True)
    number_gates = fields.Integer(required=True)
    frequency = fields.List(fields.Float, required=True)
    normalised_frequency = fields.List(fields.Float, required=True)
#    factorial = fields.Dict()
#    reduced_factorial = fields.Dict()
#    count_rate = fields.Dict()


schema = FeynmanSchema()


def WriteFeynmanJSON(FeynmanHist, out_file: string):
    """

    Args:
        FeynmanHist:
        out_file:

    Returns:

    """
    result = schema.dump(FeynmanHist)

    with open(out_file, 'w') as outfile:
        try:
            json.dump(result, outfile, indent=4, many=True)
        except ExplicitException:
            pass
        try:
            json.dump(result, outfile, indent=4, many=False)
        except ExplicitException:
            pass


def LoadFeynmanJSON(in_file: string):
    """

    Args:
        in_file: JSON file to be read in

    Returns:
        loads the FeynmanHistogram class from file
        if 2+ Histograms are saved, a list of histograms will be returned

    """

    def readFeynmanDict(data_dict):
        hist = FeynmanHistogram(data_dict['gatewidth'], data_dict['frequency'])
        hist.number_gates = data_dict['number_gates']
        hist.normalised_frequency = data_dict['normalised_frequency']

        return hist

    with open(in_file, 'r') as infile:
        dic = json.load(infile)
        try:
            data = FeynmanSchema.load(dic, many=True)
            manyHists = [readFeynmanDict(dic) for dic in data]
            return manyHists
        except ExplicitException:
            pass
        try:
            data = FeynmanSchema.load(dic, many=False)
            return readRossiDict(data)
        except ExplicitException:
            pass
