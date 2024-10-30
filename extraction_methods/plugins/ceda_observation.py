# encoding: utf-8
__author__ = "Richard Smith"
__date__ = "11 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import logging

# Third party imports
import requests
from pydantic import Field

from extraction_methods.core.extraction_method import (
    ExtractionMethod,
    Input,
    update_input,
)

LOGGER = logging.getLogger(__name__)


class CEDAObservationInput(Input):
    """CEDA Observation input model."""

    input_term: str = Field(
        default="$uri",
        description="term for method to run on.",
    )


class CEDAObservationExtract(ExtractionMethod):
    """
    .. list-table::

    Processor Name: ``ceda_observation``

    Description:
        Takes a file path and returns the ceda observation record.

    Configuration Options:
        - ``input_term``: ``REQUIRED`` term for method to run on.

    Example Configuration:
        .. code-block:: yaml
            - method: ceda_observation
                inputs:
                input_term: $url
    """

    input_class = CEDAObservationInput

    @update_input
    def run(self, body: dict) -> dict:
        r = requests.get(self.input.input_term)

        if r.status_code == 200:
            response = r.json()
            record_type = response.get("record_type")
            url = response.get("url")

            if record_type == "Dataset" and url:
                body["uuid"] = url.split("/")[-1]

        return body
