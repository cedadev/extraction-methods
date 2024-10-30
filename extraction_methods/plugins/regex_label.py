# encoding: utf-8
"""
..  _regexlabel:

Regex Label
-----------
"""
__author__ = "Rhys Evans"
__date__ = "8 Jul 2024"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"


# Python imports
import logging
import re

from pydantic import Field

from extraction_methods.core.extraction_method import (
    ExtractionMethod,
    Input,
    update_input,
)

LOGGER = logging.getLogger(__name__)


class RegexLabelInput(Input):
    """Regex Label input model."""

    input_term: str = Field(
        default="$uri",
        description="term for method to run on.",
    )
    label: str = Field(
        description="Label to add if regex passes.",
    )
    regex: str = Field(
        description="Regex to test against.",
    )
    allow_multiple: bool = Field(
        default=True,
        description="True if multiple labels are allowed.",
    )
    output_key: str = Field(
        default="label",
        description="Term for method to output to.",
    )


class RegexLabelExtract(ExtractionMethod):
    """

    .. list-table::

    Processor Name: ``regex_label``

    Description:
        Takes a list of catagory label and associated regex.

    Configuration Options:
        - ``input_term``: term for method to run on.
        - ``label``: ``REQUIRED`` Label to add if regex passes.
        - ``regex``: ``REQUIRED`` Regex to test against.
        - ``allow_multiple``: True if multiple labels are allowed.
        - ``output_key``: Term for method to output to.

    Example configuration:
        .. code-block:: yaml
            - method: regex_label
              inputs:
                label: metadata
                regex: README
                allow_multiple: true

    # noqa: W605
    """

    input_class = RegexLabelInput

    @update_input
    def run(self, body: dict) -> dict:

        match = re.search(rf"{self.input.regex}", self.input.input_term)

        if match and self.input.allow_multiple:
            body.setdefault(self.input.output_key, []).append(self.input.label)

        elif match:
            body[self.input.output_key] = self.input.label

        return body
