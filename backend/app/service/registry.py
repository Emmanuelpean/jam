"""Registry of background services.

Each service declares itself once at import via :func:`register_service`, providing its run callable
and the config defaults used to seed its :class:`~app.service.models.Service` row. The registry is the
single source of truth for a service's defaults; :func:`sync_services_to_db` creates a row for any
registered service that doesn't have one yet (without touching existing rows, so admin edits are
preserved)."""

from dataclasses import dataclass, field
from typing import Callable

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.service.models import Service, ServiceLog


@dataclass
class ServiceDefinition:
    """Everything the app knows about a background service, keyed by name.

    Attributes:
    -----------
    - `name`: Registry key; matches Service.name and the service's service_name.
    - `run`: Callable invoked as run(**parameters) to run the service.
    - `display_name`: Human-readable name seeded into the Service row.
    - `run_period_hours`: Default interval seeded into the Service row.
    - `log_model` / `log_schema`: The ServiceLog model and output schema for the log endpoints.
    - `default_parameters`: Default parameters seeded into the Service row.
    - `default_enabled`: Default is_enabled seeded into the Service row."""

    name: str
    run: Callable
    display_name: str
    run_period_hours: float
    log_model: type[ServiceLog]
    log_schema: type[BaseModel]
    default_parameters: dict = field(default_factory=dict)
    default_enabled: bool = False


SERVICE_REGISTRY: dict[str, ServiceDefinition] = {}


def register_service(
    name: str,
    run: Callable,
    *,
    log_model: type[ServiceLog],
    log_schema: type[BaseModel],
    display_name: str | None = None,
    run_period_hours: float = 24.0,
    default_parameters: dict | None = None,
    default_enabled: bool = False,
) -> None:
    """Register a background service and the defaults used to seed its Service row.
    :param name: Service registry key (matches Service.name).
    :param run: Callable invoked as run(**parameters) to run the service.
    :param log_model: The ServiceLog model for this service's logs.
    :param log_schema: The Pydantic output schema for this service's logs.
    :param display_name: Human-readable name; defaults to a title-cased name.
    :param run_period_hours: Default interval between runs, in hours.
    :param default_parameters: Default keyword arguments for the run callable.
    :param default_enabled: Whether the service is enabled when first seeded."""

    SERVICE_REGISTRY[name] = ServiceDefinition(
        name=name,
        run=run,
        display_name=display_name or name.replace("_", " ").title(),
        run_period_hours=run_period_hours,
        log_model=log_model,
        log_schema=log_schema,
        default_parameters=default_parameters or {},
        default_enabled=default_enabled,
    )


def get_service_callable(name: str) -> Callable:
    """Return the registered run callable for name.
    :param name: Service registry key.
    :raises KeyError: if no service is registered under name.
    :return: The registered run callable."""

    return SERVICE_REGISTRY[name].run


def get_service_log_view(name: str) -> tuple[type[ServiceLog], type[BaseModel]]:
    """Return the (ServiceLog model, output schema) pair registered for name.
    :param name: Service registry key.
    :raises KeyError: if no service is registered under name.
    :return: The (service-log model, output schema) tuple."""

    definition = SERVICE_REGISTRY[name]
    return definition.log_model, definition.log_schema


def sync_services_to_db(db: Session) -> int:
    """Insert a Service row for each registered service that has none yet.

    Never updates existing rows, so an admin's edits (period, parameters, enabled) are preserved
    across restarts. Idempotent: safe to call on every startup.
    :param db: Database session.
    :return: The number of rows created."""

    existing = {name for (name,) in db.query(Service.name).all()}
    created = 0
    for definition in SERVICE_REGISTRY.values():
        if definition.name in existing:
            continue
        db.add(
            Service(
                name=definition.name,
                display_name=definition.display_name,
                run_period_hours=definition.run_period_hours,
                parameters=definition.default_parameters,
                is_enabled=definition.default_enabled,
                is_running=False,
            )
        )
        created += 1
    if created:
        db.commit()
    return created
