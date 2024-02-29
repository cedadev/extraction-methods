__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import importlib
import logging
import re
import ast
import traceback


# Package imports
from extraction_methods.core.extraction_method import ExtractionMethod

LOGGER = logging.getLogger(__name__)


class LambdaExtract(ExtractionMethod):
    """

    Processor Name: ``lambda``

    Description:
        Accepts a dictionary. String values are popped from the dictionary and
        are put back into the dictionary with the ``key`` specified.

    Configuration Options:
        - ``function``: ``REQUIRED`` lambda function to be run.
        - ``output_key``: Optional name of the key you would like to output else
                          response will be merged.
        - ``exists_key``: Optional key to signify a previously extracted terms ``Default`` "$"
        - ``input_args``: Optional list of arguments for function.
                    Use $ for previously extracted terms
        - ``input_kwargs``: Optional dictionary of key word arguments for function.
                      Use $ for previously extracted terms

    Example Configuration:


    .. code-block:: yaml

        - method: lambda
          function: 'lambda x: x * x'
          input_args:
            - hello
            - world
          input_kwargs:
            hello: world
            goodbye: all

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not hasattr(self, "delimiter"):
            self.delimiter = "."

        if not hasattr(self, "exists_key"):
            self.exists_key = "$"

        if not hasattr(self, "input_args"):
            self.input_args = []

        if not hasattr(self, "input_kwargs"):
            self.input_kwargs = {}

    def run(self, body: dict, **kwargs):
        output_body = body.copy()

        try:
            function = eval(self.function)

            function_args = []
            for input_arg in self.input_args:
                if isinstance(input_arg, str) and input_arg[0] == self.exists_key:
                    if input_arg[1:] in body:
                        input_arg = body[input_arg[1:]]
                    else:
                        return body

                function_args.append(input_arg)

            function_kwargs = {}
            for input_kwarg_key, input_kwarg_value in self.input_kwargs.items():
                if isinstance(input_kwarg_value, str) and input_kwarg_value[0] == self.exists_key:
                    if input_kwarg_value[1:] in body:
                        input_kwarg_value = body[input_kwarg_value[1:]]
                    else:
                        return body

                function_kwargs[input_kwarg_key] = input_kwarg_value

            result = function(*function_args, **function_kwargs)

            if self.output_key:
                output_body[self.output_key] = result

            elif isinstance(result, dict):
                output_body |= result

            return output_body

        except Exception as e:
            LOGGER.warning(f"Lamda function: {self.function} failed.")

            return output_body