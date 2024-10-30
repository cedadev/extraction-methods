# encoding: utf-8
"""
..  _iso19115-extract:

ISO 19115 Extract
------------------
"""
__author__ = "Richard Smith"
__date__ = "28 Jul 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

# Python imports
import logging
from string import Template
from xml.etree import ElementTree as ET

# Third party imports
import requests
from pydantic import Field

from extraction_methods.core.extraction_method import (
    ExtractionMethod,
    Input,
    KeyOutputKey,
    update_input,
)

LOGGER = logging.getLogger(__name__)


class ISODateInput(Input):
    """ISO date input model."""

    url: str = Field(
        description="Url for record store.",
    )
    dates: list[KeyOutputKey] = Field(
        description="list of dates to extract.",
    )


iso19115_ns = {
    "gmd": "http://www.isotc211.org/2005/gmd",
    "gml": "http://www.opengis.net/gml/3.2",
    "gco": "http://www.isotc211.org/2005/gco",
    "gmx": "http://www.isotc211.org/2005/gmx",
    "srv": "http://www.isotc211.org/2005/srv",
    "xlink": "http://www.w3.org/1999/xlink",
}


class ISO19115Extract(ExtractionMethod):
    """
    .. list-table::

    Processor Name: ``iso19115``

    Description:
        Takes a URL and calls out to URL to retrieve the iso19115 record.

    Configuration Options:
        - ``url``: ``REQUIRED`` URL to record store.
        - ``date_terms``: List of name, key, format of date terms to retrieve from the response.

    Example configuration:
        .. code-block:: yaml
            - method: iso19115
              inputs:
                url: $url
                dates:
                  - key: './/gml:beginPosition'
                    output_key: start_datetime
    """

    input_class = ISODateInput

    @update_input
    def run(self, body: dict) -> dict:
        # Retrieve the ISO 19115 record
        response = requests.get(self.input.url)

        if not response.status_code == 200:
            LOGGER.debug("Request %s failed with response: %s", self.input.url, response.error)
            return body

        iso_record = ET.fromstring(response.text)

        # Extract the keys
        for extraction_term in self.input.dates:
            value = iso_record.find(extraction_term.key, iso19115_ns)

            if value is not None:
                body[extraction_term.output_key] = value.text

        return body
