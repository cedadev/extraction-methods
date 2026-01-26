# encoding: utf-8
""" """
__author__ = "Richard Smith"
__date__ = "19 Aug 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import logging
import os.path

# Python imports
from collections import defaultdict

# Package imports
from typing import Any

from lxml import etree  # nosec B410
from pydantic import Field

from extraction_methods.core.extraction_method import ExtractionMethod
from extraction_methods.core.types import Input, KeyOutputKey

LOGGER = logging.getLogger(__name__)


class XMLProperty(KeyOutputKey):
    """
    Model for XML property.

    """

    attribute: str = Field(
        default="",
        description="Attribute of the XML property.",
    )


class XMLInput(Input):
    """
    Model for XML Input.
    """

    input_term: str = Field(
        default="$uri",
        description="Term for method to run on.",
    )
    # template: str = Field(
    #     description="Template to follow.",
    # )
    properties: list[XMLProperty] = Field(
        description="List of properties to retrieve from the document.",
    )
    # filter_expr: str = Field(
    #     description="Regex to match against files to limit the attempts to known files.",
    # )
    namespaces: dict[str, str] = Field(
        description="Map of namespaces.",
    )


class XMLExtract(ExtractionMethod):
    """
    **Method name:** ``xml``

    Processes XML documents to extract metadata

    Example configuration:
        .. code-block:: yaml

            - method: xml
              inputs:
                properties:
                  - name: start_datetime
                    key: './/gml:beginPosition'
                    attribute: start

    # noqa: W605
    """

    input_class = XMLInput

    def run(self, body: dict[str, Any]) -> dict[str, Any]:

        # Extract the keys
        try:

            if os.path.isfile(self.input.input_term):
                xml_file = etree.parse(self.input.input_term)

            else:
                xml_file = etree.XML(self.input.input_term.encode("ascii", "ignore"))

        except (etree.ParseError, FileNotFoundError, TypeError):
            return body

        output: dict[str, list[str]] = defaultdict(list)

        for prop in self.input.properties:
            values = xml_file.findall(
                prop.key,
                self.input.namespaces,
            )

            for value in values:
                if value is not None:

                    if prop.attribute:
                        v = value.get(prop.attribute, "")

                    else:
                        v = value.text

                    if v and v not in output[prop.output_key]:
                        output[prop.output_key].append(v.strip())

            if output[prop.output_key]:
                body[prop.output_key] = (
                    output[prop.output_key][0]
                    if len(output[prop.output_key]) == 1
                    else output[prop.output_key]
                )

        return body
