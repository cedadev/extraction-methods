# encoding: utf-8
"""
..  _xml-extract:

XML Extract
------------
"""
__author__ = "Richard Smith"
__date__ = "19 Aug 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import logging

# Python imports
from collections import defaultdict
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError

from pydantic import Field

# Package imports
from extraction_methods.core.extraction_method import (
    ExtractionMethod,
    update_input,
)
from extraction_methods.core.types import Input, KeyOutputKey

LOGGER = logging.getLogger(__name__)


class XMLProperty(KeyOutputKey):
    """XML property model."""

    attribute: str = Field(
        default="",
        description="Attribute of the XML property.",
    )


class XMLInput(Input):
    """XML input model."""

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
    namespaces: dict = Field(
        description="Map of namespaces.",
    )


class XMLExtract(ExtractionMethod):
    """
    .. list-table::

    Processor Name: ``xml``

    Description:
        Processes XML documents to extract metadata

    Configuration Options:
        - ``input_term``: Term for method to run on.
        - ``template``: ``REQUIRED`` Template to follow.
        - ``properties``: ``REQUIRED`` List of properties to retrieve from the document.
        - ``namespaces``: ``REQUIRED`` Map of namespaces.

    Extraction Keys:
        Extraction keys should be a map.

        .. list-table::

            * - Name
              - Description
            * - ``key``
              - Key of the property. Passed to
                `xml.etree.ElementTree.find() <https://docs.python.org/3/library/xml.etree.elementtree.html?highlight=find#xml.etree.ElementTree.ElementTree.find>`_
                and also supports `xpath formatted <https://docs.python.org/3/library/xml.etree.elementtree.html#xpath-support>`_ accessors
            * - ``output_key``
              - Key to output to.
            * - ``attribute``
              - Allows you to select from the element attribute. In the absence of this value, the default behaviour is to access the text value of the key.
                In some cases, you might want to access and attribute of the element.

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

    def run(self, body: dict) -> dict:
        # Extract the keys
        try:
            if isinstance(self.input.input_term, str):
                xml_file = ElementTree.parse(self.input.input_term)

            else:
                xml_file = ElementTree.XML(self.input.input_term)

        except (ParseError, FileNotFoundError, TypeError):
            return body

        output = defaultdict(list)

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

            if output[prop.output_key] and len(output[prop.output_key]) == 1:
                output[prop.output_key] = output[prop.output_key][0]

            if not output[prop.output_key]:
                output[prop.output_key] = None

        body |= output

        return body
