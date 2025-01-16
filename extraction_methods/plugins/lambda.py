__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging
from ast import literal_eval

from pydantic import Field

from extraction_methods.core.extraction_method import (
    ExtractionMethod,
    update_input,
)
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)


class LambdaInput(Input):
    """Lambda input model."""

    function: str = Field(
        description="lambda function to be run.",
    )
    args: list = Field(
        default=[],
        description="list of arguments for function.",
    )
    kwargs: dict = Field(
        default={},
        description="dictionary of key word arguments for function.",
    )
    output_key: str = Field(
        default="label",
        description="key to output to.",
    )


class LambdaExtract(ExtractionMethod):
    """
    .. list-table::

    Processor Name: ``lambda``

    Description:
        Accepts a dictionary. String values are popped from the dictionary and
        are put back into the dictionary with the ``key`` specified.

    Configuration Options:
        - ``function``: ``REQUIRED`` lambda function to be run.
        - ``output_key``: Optional name of the key you would like to output else
                          response will be merged.
        - ``args``: Optional list of arguments for function.
                    Use $ for previously extracted terms
        - ``kwargs``: Optional dictionary of key word arguments for function.
                      Use $ for previously extracted terms

    Example Configuration:
        .. code-block:: yaml
            - method: lambda
            function: 'lambda x: x * x'
            args:
                - hello
                - $world
            kwargs:
                hello: world
                goodbye: all
    """

    input_class = LambdaInput

    # @update_input
    def run(self, body: dict) -> dict:
        output_body = body.copy()

        # try:
        function = eval(self.input.function)

        result = function(*self.input.args, **self.input.kwargs)

        if self.input.output_key:
            output_body[self.input.output_key] = result

        elif isinstance(result, dict):
            output_body |= result

        # except Exception as e:
        #     LOGGER.warning(f"Lamda function: {self.input.function} failed.")

        return output_body
