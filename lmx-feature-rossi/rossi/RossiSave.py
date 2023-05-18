from marshmallow import Schema, fields, post_load, ValidationError
from lmx.rossi.RossiHistogram import RossiHistogram
import json
import pickle


def PickleRossi(data, file):
    with open(file, "wb") as out_file:
        pickle.dump(data, out_file)


def UnpickleRossi(file):
    with open(file, "rb") as in_file:
        RossiHist = pickle.load(in_file)
        return RossiHist


class RossiSchema(Schema):
    reset_time = fields.Float(required=True)
    num_bins = fields.Integer(required=True)
    freq = fields.List(fields.Float, required=True)
    bins = fields.List(fields.Float, required=True)
    sgl_cov = fields.List(fields.Float)
    sgl_opts = fields.List(fields.Float)
    dbl_cov = fields.List(fields.Float)
    dbl_opts = fields.List(fields.Float)


schema = RossiSchema()


def WriteRossiJSON(RossiHist, out_file: str):
    """

    Args:
        RossiHist:
        out_file:

    Returns:

    """
    result = schema.dump(RossiHist)

    with open(out_file, 'w') as outfile:
        try:
            json.dump(result, outfile, indent=4, many=True)
        except ExplicitException:
            pass
        try:
            json.dump(result, outfile, indent=4, many=False)
        except ExplicitException:
            pass


def LoadRossiJSON(in_file: str):
    """

    Args:
        in_file: JSON file to be read in

    Returns:
        loads the RossiHistogram class from file
        if 2+ Histograms are saved, a list of histograms will be returned

    """
    def readRossiDict(data_dict):
        hist = RossiHistogram(data_dict['reset_time'], data_dict['freq'])
        hist.num_bins = data_dict['num_bins']
        hist.bins = data_dict['bins']
        hist.single_opts = data_dict['sgl_opts']
        hist.single_covariance = data_dict['sgl_cov']
        hist.double_opts = data_dict['dbl_opts']
        hist.double_covariance = data_dict['dbl_cov']
        return hist

    with open(in_file, 'r') as infile:
        dic = json.load(infile)
        try:
            data = RossiSchema.load(dic, many=True)
            manyHists = [readRossiDict(dic) for dic in data]
            return manyHists
        except ExplicitException:
            pass
        try:
            data = RossiSchema.load(dic, many=False)
            return readRossiDict(data)
        except ExplicitException:
            pass
