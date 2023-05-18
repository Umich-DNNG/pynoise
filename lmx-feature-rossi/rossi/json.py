# standard imports
from typing import List
from marshmallow import Schema, ValidationError, fields, validates, post_load
import json

# local imports
from lmx.rossi.RossiHistogram import RossiHistogram
from smores.schema.BaseSchema import BaseSchema


class RossiSchema(BaseSchema):
    """
    Schema for saving RossiHistogram(s) to a JSON file
    """
    object_ = RossiHistogram

    reset_time = fields.Float(required=True)
    frequency = fields.List(fields.Float, required=True)

    class Meta:
        ordered = True


def writeRossiToJSON(data: RossiHistogram or List[RossiHistogram], file: str, indent: int = None):
    """Save Rossi data through python marshmallow to JSON file

        Arguments:
            data: RossiHistogram(s)
            file: name of file to be saved to
            indent: The amount of indentations in JSON output
    """
    schema = RossiSchema()

    if file.endswith(".json") is False:
        file = file + ".json"

    if isinstance(data, RossiHistogram):
        result = schema.dump(data, many=False)
    elif isinstance(data, List):
        if isinstance(data[0], RossiHistogram):
            result = schema.dump(data, many=True)
        else:
            raise TypeError("List provided does not contain RossiHistogram types")
    else:
        raise TypeError("A single or list of RossiHistogram types not provided")

    with open(file, 'w') as outfile:
        json.dump(result, outfile, indent=indent)


def loadRossiFromJSON(file: str):
    """Load Rossi data through python marshmallow from JSON file

        Arguments:
            file: JSON file to be read in

        Returns:
            loads the RossiHistogram type(s) from file
            if 2+ Histograms are saved, a list of histograms will be returned
    """
    schema = RossiSchema()

    if file.endswith(".json") is False:
        file = file + ".json"

    with open(file, 'r') as infile:
        data = json.load(infile)
        if isinstance(data, List):
            return schema.load(data, many=True)
        else:
            return schema.load(data, many=False)
