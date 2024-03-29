# encoding: utf-8
"""
..  _regex:

Regex
------
"""
__author__ = "Richard Smith"
__date__ = "27 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


# Python imports
from collections import defaultdict
import os
import json
import logging
from typing import Optional

from extraction_methods.core.extraction_method import ExtractionMethod

LOGGER = logging.getLogger(__name__)


class JsonFileExtract(ExtractionMethod):
    """

    .. list-table::

        * - Processor Name
          - ``json``

    Description:
        Takes an input list of string to extract from the json file.

    Configuration Options:
        - ``terms``: List of terms to extract


    Example configuration:
        .. code-block:: yaml

            - method: json
              inputs:
                dirpath: /path/to/file.json
                terms:
                  - mip_era

    """

    def get_facet_values(self) -> list:
        output = defaultdict(set)

        for filepath in os.listdir(self.dirpath):

            with open(os.path.join(self.dirpath, filepath), "r") as file:
                item = json.load(file)

                item_properties = item["properties"]

                for facet in self.terms:
                    if facet in item_properties:
                        if isinstance(item_properties[facet], list):
                            output[facet].update(item_properties[facet])
                        else:
                            output[facet].add(item_properties[facet])

        for facet in self.terms:
            output[facet] = list(output[facet])

        return output

    @staticmethod
    def get_spatial_extent(item_list: list) -> dict:
        ...

    @staticmethod
    def get_temporal_extent(item_list: list) -> dict:
        start_datetime = []
        end_datetime = []
        datetime = []

        for item in item_list:
            start_datetime.append(item["properties"].get("start_datetime"))
            end_datetime.append(item["properties"].get("end_datetime"))
            datetime.append(item["properties"].get("datetime"))

        start_datetime = list(set(start_datetime))
        end_datetime = list(set(end_datetime))
        datetime = list(set(datetime))

    def get_extent(self, file_id: str) -> dict:
        item_list = []
        with open(self.filepath, "r") as file:
            file_data = json.load(file)

            for item in file_data:
                if item["collection_id"] == file_id:
                    item_list.append(item)

        # spatial_extent = self.get_spatial_extent(item_list)
        # temporal_extent = self.get_temporal_extent(item_list)

    def run(self, body: dict, **kwargs) -> dict:
        output = self.get_facet_values()

        if output:
            body |= output

        # No need to include extents since the example scanner has none.

        return body
