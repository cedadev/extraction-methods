# encoding: utf-8
"""
..  _path_parts:

Path Parts
------
"""
__author__ = "Richard Smith"
__date__ = "27 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


# Python imports
import logging
from pathlib import Path

from pydantic import Field

from extraction_methods.core.extraction_method import (
    ExtractionMethod,
    Input,
    update_input,
)

LOGGER = logging.getLogger(__name__)


class PathPartsInput(Input):
    """path parts input model."""

    path: str = Field(
        default="$uri",
        description="path for method to run on.",
    )
    skip: int = Field(
        default=0,
        description="number of path parts to skip.",
    )


class PathPartsExtract(ExtractionMethod):
    """

    .. list-table::

        * - Processor Name
          - ``path_parts``

    Description:
        Extracts the parts of a given path skipping ``skip`` number
        of top level parts.

    Configuration Options:
        - ``skip``: The number of path parts to skip. ``default: 0``


    Example configuration:
        .. code-block:: yaml

            - method: path_parts
              inputs:
                input_term: $uri
                skip: 2

    """

    input_class = PathPartsInput

    @update_input
    def run(self, body: dict) -> list:
        path = Path(self.input.path)

        parts = list(path.parts)[self.input.skip :]

        body["filename"] = parts.pop()

        dir_level = 1
        for part in parts:
            body[f"_dir{dir_level}"] = part
            dir_level += 1

        return body
