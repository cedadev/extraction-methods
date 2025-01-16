# encoding: utf-8
"""

"""
__author__ = "Rhys Evans"
__date__ = "07 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"

from abc import ABC, abstractmethod
from typing import Any

import pkg_resources
from pydantic import BaseModel, Extra, Field, model_validator
from .types import Input, DummyInput
from collections.abc import Iterator

def update_input(func) -> dict:
    """
    Wrapper to update extration method inputs with body values before run
    """

    def wrapper(self, body):
        self._input.update_attrs(body)
        return func(self, body)

    return wrapper


class SetInput:
    input_class: Input = Input
    dummy_input_class: Input = DummyInput

    def __init__(self, *args, **kwargs):
        """
        Set the kwargs to generate instance attributes of the same name

        :param kwargs:
        """
        defaults = {
            key: value.get_default()
            for key, value in self.input_class.model_fields.items()
            if value.get_default()
        }

        self._input = self.dummy_input_class(**defaults | kwargs)


class SetEntryPointsMixin:
    entry_point_group: str
    entry_points: dict = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for entry_point in pkg_resources.iter_entry_points(self.entry_point_group):
            self.entry_points[entry_point.name] = entry_point


class ExtractionMethod(SetInput, ABC):
    """
    Class to act as a base for all extracion methods. Defines the basic method signature
    and ensure compliance by all subclasses.
    """

    def _run(self, body: dict) -> dict:
        """
        Set input then run the extration method

        :param body:
        :param kwargs:

        :return body:
        """

        self._input.update_attrs(body)
        self.input = self.input_class(**self._input.dict())

        return self.run(body)

    @abstractmethod
    def run(self, body: dict) -> dict:
        """
        Run the extration method

        :param body:
        :param kwargs:

        :return body:
        """

class Backend(SetInput, ABC):
    """
    Class to act as a base for all extracion methods. Defines the basic method signature
    and ensure compliance by all subclasses.
    """

    def _run(self, body: dict) -> Iterator[dict]:
        """
        Set input then run the extration method

        :param body:
        :param kwargs:

        :return body:
        """

        self._input.update_attrs(body)
        self.input = self.input_class(**self._input.dict())

        return self.run(body)

    @abstractmethod
    def run(self, body: dict) -> Iterator[dict]:
        """
        Run the extration method

        :param body:
        :param kwargs:

        :return body:
        """