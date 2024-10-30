__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging
from datetime import datetime

from pydantic import BaseModel, Field

from extraction_methods.core.extraction_method import (
    ExtractionMethod,
    Input,
    update_input,
)

LOGGER = logging.getLogger(__name__)


class DateTerm(BaseModel):
    """Date  model with added format."""

    input_term: str = Field(
        description="Term to run method on.",
    )
    format: str = Field(
        default="%Y-%m-%dT%H:%M:%SZ",
        description="Format of the date.",
    )
    output_key: str = Field(
        default="datetime",
        description="Key to output to.",
    )


class ISODateInput(Input):
    """path parts input model."""

    dates: list[DateTerm] = Field(
        default=[],
        description="List of date terms.",
    )


class ISODateExtract(ExtractionMethod):
    """
    .. list-table::

    Processor Name: ``isodate``

    Description:
        Takes the source dict and the key to access the date and
        converts the date to ISO 8601 Format.

        e.g.

        ``YYYY-MM-DDTHH:MM:SS.ffffff``, if microsecond is not 0
        ``YYYY-MM-DDTHH:MM:SS``, if microsecond is 0

        If the date format cannot be parsed, it is removed from the source dict with
        an error logged.

    Configuration Options:
        - ``date_terms``: `REQUIRED` List keys to the date value. Using a list allows processing of multiple dates.
        - ``format``: Optional format string. Default behaviour uses `dateutil.parser.parse <https://dateutil.readthedocs.io/en/stable/parser.html#dateutil.parser.parse>`_.
          If a format string is supplied, this will change to use `datetime.datetime.strptime <https://docs.python.org/3/library/datetime.html#datetime.datetime.strptime>`_.

    Example Configuration:
        .. code-block:: yaml
            - method: isodate
              inputs:
                dates:
                  - key: $datetime
                    output_key: date
                    format: "%Y-%m-%dT%H:%M:%S"
                  - key: 2012-12-12
                    format: "%Y-%m-%d"
    """

    input_class = ISODateInput

    @update_input
    def run(self, body: dict) -> dict:
        """
        :param body: dict containing the date value

        :return: the source dict with the date converted to ISO8601 format.
        """

        for date_term in self.input.date_terms:

            if not date_term:
                LOGGER.error("%s not present in %s", date_term.input_term, body)

            else:

                try:
                    date_iso = datetime.strptime(date_term.input_term, date_term.format).isoformat()
                    body[date_term.output_key] = date_iso

                except ValueError:
                    LOGGER.error(
                        "date_term: %s doesn't match format: %s",
                        date_term.input_term,
                        date_term.format,
                    )

        return body
