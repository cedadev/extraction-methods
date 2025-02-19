# encoding: utf-8
"""
..  _extraction-methods:

Extraction Method Models
------------------------
"""
__author__ = "Rhys Evans"
__date__ = "07 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from typing import Any

import pkg_resources

from .types import DummyInput, Input


def update_input(
    func: Callable[[Any, dict[str, Any]], Any]
) -> Callable[[Any, dict[str, Any]], Any]:
    """
    Wrapper to update inputs with body values before run.

    :param func: function that wrapper is to be run on
    :type func: Callable

    :return: function that wrapper is to be run on
    :rtype: Callable
    """

    def wrapper(self, body: dict[str, Any]) -> Any:  # type: ignore[no-untyped-def]
        self._input.update_attrs(body)
        return func(self, body)

    return wrapper


class SetInput:
    """
    Class to set input attribute from kwargs.
    """

    input_class: Any = Input
    dummy_input_class: Any = DummyInput

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Set ``input`` attribute to instance of ``dummy_input_class`` with
        default values overrided by kwargs.

        :param args: fuction arguments
        :type func: Any
        :param kwargs: fuction keyword arguments
        :type func: Any
        """
        defaults = {
            key: value.get_default()
            for key, value in self.input_class.model_fields.items()
            if value.get_default()
        }

        self._input = self.dummy_input_class(**defaults | kwargs)


class SetEntryPointsMixin:
    """
    Mixin to set ``entry_points`` attribute.
    """

    entry_point_group: str
    entry_points: dict[str, pkg_resources.EntryPoint] = {}

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Set ``entry_points`` attribute with entrypoints in ``entry_point_group`` attribute.

        :param args: fuction arguments
        :type func: Any
        :param kwargs: fuction keyword arguments
        :type func: Any
        """
        super().__init__(*args, **kwargs)

        for entry_point in pkg_resources.iter_entry_points(self.entry_point_group):
            self.entry_points[entry_point.name] = entry_point


class ExtractionMethod(SetInput, ABC):
    """
    Class to act as a base for all extracion methods. Defines the basic method signature
    and ensure compliance by all subclasses.
    """

    def _run(self, body: dict[str, Any]) -> dict[str, Any]:
        """
        Update ``input`` attribute then run the method.

        :param body: current generated properties
        :type body: dict

        :return: updated body dict
        :rtype: dict
        """

        self._input.update_attrs(body)
        self.input = self.input_class(**self._input.dict())

        return self.run(body)

    @abstractmethod
    def run(self, body: dict[str, Any]) -> dict[str, Any]:
        """
        Run the method.

        :param body: current generated properties
        :type body: dict

        :return: updated body dict
        :rtype: dict
        """


class Backend(SetInput, ABC):
    """
    Class to act as a base for Backends. Defines the basic method signature
    and ensure compliance by all subclasses.
    """

    def _run(self, body: dict[str, Any]) -> Iterator[dict[str, Any]]:
        """
        Update ``input`` attribute then run the backend.

        :param body: current generated properties
        :type body: dict

        :return: updated body dict
        :rtype: dict
        """

        self._input.update_attrs(body)
        self.input = self.input_class(**self._input.dict())

        return self.run(body)

    @abstractmethod
    def run(self, body: dict[str, Any]) -> Iterator[dict[str, Any]]:
        """
        Run the backend.

        :param body: current generated properties
        :type body: dict

        :return: updated body dict
        :rtype: dict
        """
