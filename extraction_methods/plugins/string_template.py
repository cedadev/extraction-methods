__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging
import re

from pydantic import Field

# Package imports
from extraction_methods.core.extraction_method import (
    ExtractionMethod,
    update_input,
)
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)


class StringTemplateInput(Input):
    """String template input model."""

    template: str = Field(
        description="Template to follow.",
    )
    descructive: bool = Field(
        default=False,
        description="True if terms should be removed after templating.",
    )
    output_key: str = Field(
        description="key to output to.",
    )


class StringTemplateExtract(ExtractionMethod):
    """
    .. list-table::

    Processor Name: ``string_template``

    Description:
        Accepts a template and output_key. terms are added to the template.

    Configuration Options:
        - ``template``: ``REQUIRED`` Template to follow.
        - ``descructive``: True if terms should be removed after templating.
        - ``output_key``: ``REQUIRED`` key to output to.

    Example Configuration:
        .. code-block:: yaml
            - method: string_template
            inputs:
                template: {hello}/{goodbye}/{hello}/bonjour.html
                output_key: manifest_url
    """

    input_class = StringTemplateInput

    @update_input
    def run(self, body: dict) -> dict:
        terms = re.findall("{(.*?)}", self.input.template)

        if self.input.descructive:
            format_terms = {term: body.pop(term, "") for term in terms}
        else:
            format_terms = {term: body.get(term, "") for term in terms}

        body[self.input.output_key] = self.input.template.format(**format_terms)

        return body
