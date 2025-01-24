__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging
import re

from pydantic import BaseModel, Field

# Package imports
from extraction_methods.core.extraction_method import (
    ExtractionMethod,
    update_input,
)
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)

class STACExtension(BaseModel):
    """STAC Extension model."""

    url: str = Field(
        description="Extension URL.",
    )
    prefix: str = Field(
        description="Extension prefix.",
    )
    properties: list[str] = Field(
        description="Extension properties.",
    )

class STACExtensionInput(Input):
    """STAC Extension input model."""

    extensions: list[STACExtension] = Field(
        description="List of extensions.",
    )


class STACExtensionExtract(ExtractionMethod):
    """
    .. list-table::

    Processor Name: ``stac_extension``

    Description:
        Accepts a list of extensions which contain url, prefix and
        list of properties.

    Configuration Options:
        - ``extensions``: ``REQUIRED`` List of extensions.

    Example Configuration:
        .. code-block:: yaml
            - method: stac_extension
            inputs:
                extensions:
                  - url: hello.com/v1.0.0/world.json
                    prefix: hello
                    properties:
                      - foo
                      - bar
    """

    input_class = STACExtensionInput

    @update_input
    def run(self, body: dict) -> dict:
        extension_urls = []
        for extension in self.input.extensions:
            extension_urls.append(extension.url)
            for property_name in extension.properties:
                if property_name in body:
                    body[f"{extension.prefix}:{property_name}"] = body.pop(property_name)

        body["stac_extensions"] = body.get("stac_extensions", []) + extension_urls

        return body
