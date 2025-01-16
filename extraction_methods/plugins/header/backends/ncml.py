# encoding: utf-8
"""
Metadata extraction backend for NcML (XML) description files.
"""
__author__ = "David Huard"
__date__ = "June 2022"
__copyright__ = "Copyright 2022 Ouranos"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "huard.david@ouranos.ca"

import logging
import subprocess
from urllib.parse import urlparse

import requests
from lxml.etree import XMLParser, fromstring
from pydantic import Field

from extraction_methods.core.extraction_method import (
    SetInput,
    update_input,
)
from extraction_methods.core.types import Input, NameKeyTerm

LOGGER = logging.getLogger(__name__)


class NcMLHeaderInput(Input):
    """Intake backend input model."""

    input_term: str = Field(
        default="$uri",
        description="term for method to run on.",
    )
    requests_params: dict = Field(
        default={"catalog": None, "dataset": None},
        description="params for reqests.",
    )
    namespaces: dict = Field(
        default={"ncml": "http://www.unidata.ucar.edu/namespaces/netcdf/ncml-2.2"},
        description="NcML namespaces.",
    )
    attributes: list[NameKeyTerm] = Field(
        default={},
        description="attributes to be extracted.",
    )


class NcMLHeader(SetInput):
    """
    NcMLHeader
    ----

    Backend Name: ``NcMLHeader``
    """

    input_class = NcMLHeaderInput

    @update_input
    def run(self, body: dict) -> dict:
        """
        Takes a filepath and list of attributes and extracts the metadata.

        :param file: file-like object
        :param attributes: attributes to extract
        :param backend_kwargs: {}

        :return: Dictionary of extracted attributes
        """

        # Convert response to an XML etree.Element
        content = self.get_ncml()
        elemement = fromstring(content, parser=XMLParser(encoding="UTF-8"))

        output = {}
        for attribute in self.input.attributes:

            # Execute xpath expression
            value = elemement.xpath(attribute.key, namespaces=self.input.namespaces)

            if value:
                output[attribute.name] = value[0]

        return output

    def get_ncml(self) -> bytes:
        """Get the NcML file description."""

        parse_result = urlparse(self.input.input_term)

        if parse_result.netloc:
            return self.get_ncml_from_thredds()

        return self.get_ncml_from_fs()

    def get_ncml_from_thredds(self) -> bytes:
        """Read NcML response from THREDDS server.

        Returns
        -------
        bytes
        NcML content
        """

        r = requests.get(self.input.input_term, params=self.input.params)
        r.raise_for_status()
        return r.content

    def get_ncml_from_fs(self) -> bytes:
        """Return NcML file description using `ncdump` utility."""

        cmd = ["ncdump", "-hx", self.input.input_term]
        proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        return proc.stdout.read()
