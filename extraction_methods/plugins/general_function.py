__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import importlib
import logging

from pydantic import Field

# Package imports
from extraction_methods.core.extraction_method import (
    ExtractionMethod,
    Input,
    update_input,
)

LOGGER = logging.getLogger(__name__)


class GeneralFunctionInput(Input):
    """General Function input model."""

    function: str = Field(
        description="Path to function seperatated my delimieter.",
    )
    delimiter: str = Field(
        default=".",
        description="text delimiter to put between module/function names.",
    )
    args: list[str] = Field(
        default=[],
        description="list of arguments for function.",
    )
    kwargs: dict = Field(
        default={},
        description="dictionary of key word arguments for function.",
    )
    output_key: str = Field(
        default="",
        description="key to output to, else response will be merged with body.",
    )


class GeneralFunctionExtract(ExtractionMethod):
    """
    .. list-table::

    Processor Name: ``general_function``

    Description:
        Accepts a dictionary. String values are popped from the dictionary and
        are put back into the dictionary with the ``key`` specified.

    Configuration Options:
        - ``function``: ``REQUIRED`` name of function.
        - ``delimiter``: Optional text delimiter to put between module/function
                        names ``Default`` "."
        - ``output_key``: Optional name of the key you would like to output else
                          response will be merged.
        - ``args``: Optional list of arguments for function.
        - ``kwargs``: Optional dictionary of key word arguments for function.

    Example Configuration:
        .. code-block:: yaml
            - method: general_function
            funtion: import.path.to.the.fuction
            args:
                - hello
                - world
            kwargs:
                hello: world
                goodbye: all
    """

    input_class = GeneralFunctionInput

    @update_input
    def run(self, body: dict) -> dict:
        output_body = body.copy()

        module_name, function_name = self.input.function.rsplit(self.input.delimiter, 1)

        module = importlib.import_module(module_name)

        function = getattr(module, function_name)

        result = function(*self.input.args, **self.input.kwargs)

        if self.input.output_key:
            output_body[self.input.output_term] = result

        elif isinstance(result, dict):
            output_body |= result

        return output_body
