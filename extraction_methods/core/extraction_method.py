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
from pydantic import BaseModel, Field, model_validator


class KeyOutputKey(BaseModel):
    """Model for key and output key pairs."""

    key: str
    output_key: str = ""

    @model_validator(mode="after")
    def set_default_key(self):
        """Set the default for key"""
        if self.output_key == "":
            self.output_key = self.key
        return self


class Input(BaseModel):
    """Extraction method input."""

    exists_key: str = Field(
        default="$",
        description="Key to signify a previously extracted terms.",
    )

    exists_delimiter: str = Field(
        default=".",
        description="Delimiter for nested exists terms.",
    )

    def update_attr(self, value: Any, body: dict) -> Any:
        """Update an attribute"""
        if isinstance(value, str) and value[0] == self.exists_key:
            return body[value[1:]]

        if isinstance(value, dict):
            return self.update_dict_attr(value, body)

        if isinstance(value, list):
            return self.update_list_attr(value, body)

        return value

    def update_dict_attr(self, input_dict: dict, body: dict) -> dict:
        """Update a dictionary of attributes"""
        for key, value in input_dict:
            input_dict[key] = self.update_attr(value, body)

        return input_dict

    def update_list_attr(self, input_list: list, body: dict) -> list:
        """Update a list of attributes"""
        for key, value in enumerate(input_list):
            input_list[key] = self.update_attr(value, body)

        return input_list

    def update_attrs(self, body: dict) -> None:
        """
        Update instance attributes from body

        :param body:
        """
        for key, value in self.__dict__.items():
            setattr(self, key, self.update_attr(value, body))


class Backend(BaseModel):
    name: str = Field(
        description="Name of backend.",
    )
    inputs: dict = Field(
        default={},
        description="Inputs for backend.",
    )


def update_input(func) -> dict:
    """
    Wrapper to update extration method inputs with body values before run
    """

    def wrapper(self, body):
        self.input.update_attrs(body)
        return func(self, body)

    return wrapper


class SetInput(ABC):
    input_class: Input

    def __init__(self, **kwargs):
        """
        Set the kwargs to generate instance attributes of the same name

        :param kwargs:
        """
        super().__init__(**kwargs)
        self.input = self.input_class(**kwargs)


class SetEntryPoints(ABC):
    entry_point_group: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entry_points = {}

        for entry_point in pkg_resources.iter_entry_points(self.entry_point_group):
            self.entry_points[entry_point.name] = entry_point


class ExtractionMethod(SetInput):
    """
    Class to act as a base for all extracion methods. Defines the basic method signature
    and ensure compliance by all subclasses.
    """

    @abstractmethod
    def run(self, body: dict) -> dict:
        """
        Run the extration method

        :param body:
        :param kwargs:

        :return body:
        """
