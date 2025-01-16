# encoding: utf-8
__author__ = "Rhys Evans"
__date__ = "24 May 2022"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"

import logging

# Third party imports
from pydantic import Field

from typing import Any
from extraction_methods.core.extraction_method import (
    ExtractionMethod,
    SetEntryPointsMixin,
    update_input,
)
from extraction_methods.core.types import (
    Backend,
    Input,
)

LOGGER = logging.getLogger(__name__)


class AssetInput(Input):
    """Asset input model."""

    backend: Backend = Field(
        description="Label to add if regex passes.",
    )
    extraction_methods: list[Any] = Field(
        default=[],
        description="Extraction methods to run on assets.",
    )
    output_key: str = Field(
        default="assets",
        description="term for method to output to.",
    )


class AssetExtract(SetEntryPointsMixin, ExtractionMethod):
    """
    Description:
        Asset extraction method.

    Configuration Options:
        - ``backend``: Backend name and inputs.
        - ``extraction_methods``: Extraction methods to run on assets.
        - ``output_key``: key to output to.

    Configuration Example:

        .. code-block:: yaml

                name: elasticsearch
                inputs:
                  backend: elasticsearch
                  inputs:
                    index
                    connection_kwargs:
                      hosts: ['host1:9200','host2:9200']
                  extraction_methods:
                    - method: default
                      inputs:
                        defaults:
                          hello: world
    """

    input_class = AssetInput
    entry_point_group: str = "extraction_methods.assets.backends"




    @update_input
    def run(self, body: dict) -> dict:

        output = {}
        backend_entry_point = self.entry_points.get(self.input.backend.name).load()
        backend = backend_entry_point(**self.input.backend.inputs)
        assets = backend._run(body)

        for asset in assets:
            for extraction_method in self.input.extraction_methods:
                asset = extraction_method._run(asset)
            output[asset["href"]] = asset

        body[self.input.output_key] = body.get(self.input.output_key, {}) | output

        return body
