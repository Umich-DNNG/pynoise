# standard imports
from typing import List
from marshmallow import Schema, ValidationError, fields, validates, post_load
import json

# local imports
from lmx.feynman.FeynmanHistogram import FeynmanHistogram
from smores.schema.BaseSchema import BaseSchema


class FeynmanSchema(BaseSchema):
    """
    Schema for saving FeynmanHistogram(s) to a JSON file
    """
    object_ = FeynmanHistogram

    gatewidth = fields.Float(required=True)
    frequency = fields.List(fields.Float, required=True)

    class Meta:
        ordered = True


def writeFeynmanToJSON(data: FeynmanHistogram or List[FeynmanHistogram], file: str, indent: int = None):
    """Save Feynman data through python marshmallow to JSON file

    Args:
        data: FeynmanHistogram(s)
        file: name of file to be saved to
        indent: The amount of indentations in JSON output
    """
    schema = FeynmanSchema()

    if file.endswith(".json") is False:
        file = file + ".json"

    if isinstance(data, FeynmanHistogram):
        result = schema.dump(data, many=False)
    elif isinstance(data, List):
        if isinstance(data[0], FeynmanHistogram):
            result = schema.dump(data, many=True)
        else:
            raise TypeError("List provided does not contain FeynmanHistogram types")
    else:
        raise TypeError("A single or list of FeynmanHistogram types not provided")

    with open(file, 'w') as outfile:
        json.dump(result, outfile, indent=indent)


def loadFeynmanFromJSON(file: str):
    """Load Feynman data through python marshmallow from JSON file

       Arguments:
            file: JSON file to be read in

       Returns:
           loads the FeynmanHistogram type(s) from file
           if 2+ Histograms are saved, a list of histograms will be returned
    """
    schema = FeynmanSchema()

    if file.endswith(".json") is False:
        file = file + ".json"

    with open(file, 'r') as infile:
        data = json.load(infile)
        if isinstance(data, List):
            return schema.load(data, many=True)
        else:
            return schema.load(data, many=False)
