"""Module defining the ServiceLog base class for service logs."""

from sqlalchemy import Column, String, Float, Boolean, TIMESTAMP


class ServiceLog(object):
    """Base class for service logs.

    Attributes:
    -----------
    - `run_duration` (float, optional): Duration of the service run.
    - `run_datetime` (datetime): Date and time of the service run.
    - `is_success` (bool): Indicates whether the service run was successful.
    - `error_message` (str, optional): Error message if the service run failed."""

    run_duration = Column(Float, nullable=True)
    run_datetime = Column(TIMESTAMP(timezone=True), nullable=False)
    is_success = Column(Boolean, nullable=True)
    error_message = Column(String, nullable=True)
