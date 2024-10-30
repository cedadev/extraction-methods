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
import tempfile
import zipfile

from pydantic import Field

from extraction_methods.core.extraction_method import (
    ExtractionMethod,
    Input,
    KeyOutputKey,
    update_input,
)

LOGGER = logging.getLogger(__name__)


class ZipInput(Input):
    """Zip input model."""

    input_term: str = Field(
        default="$uri",
        description="term for method to run on.",
    )
    inner_files: list[KeyOutputKey] = Field(
        default=[],
        description="list of inner zipped files to be read.",
    )
    output_key: str = Field(
        default="",
        description="key to output to.",
    )


class ZipExtract(ExtractionMethod):
    """
    .. list-table::

        * - Processor Name
          - ``zip``

    Description:
        Open a zip file and read inner files

    Configuration Options:
        - ``input_term``: List of keys to retrieve from the document.
        - ``inner_files``: Lost of inner zipped files to be read.
        - ``output_key``: key to output to.

    Example configuration:
        .. code-block:: yaml

            - method: xml
              inputs:
                input_term: /path/to/a/file
                inner_files:
                  - key: hello.txt
                    output_key: world

    # noqa: W605
    """

    input_class = ZipInput

    @update_input
    def run(self, body: dict) -> dict:
        # Extract the keys
        try:
            with zipfile.ZipFile(self.input.input_term) as z:
                output = {}
                for inner_file in self.input.inner_files:
                    output[inner_file.output_key] = z.read(inner_file.key)

                if not output:
                    output = z.read()

        except FileNotFoundError:
            output = tempfile.TemporaryFile()

        if self.input.output_key:
            output = {self.input.output_key: output}

        body |= output

        return body
