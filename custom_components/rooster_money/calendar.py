"""Defines a CalendarEntity for Rooster Money job's"""

import logging
from datetime import datetime, timezone
from pyroostermoney import RoosterMoney

from pyroostermoney.child import ChildAccount, Job
import pytz
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import UndefinedType
from .rooster_base import RoosterChildEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Rooster Money session."""
    # Get a list of all children in account
    entities = []
    for child in hass.data[DOMAIN][config_entry.entry_id].children:
        entities.append(
            ChildJobCalendar(
                account=child,
                entity_id="jobs",
                session=hass.data[DOMAIN][config_entry.entry_id],
            )
        )

    async_add_entities(entities, True)


def build_calendar_event(job: Job) -> CalendarEvent:
    """Converts a job to a calendar event."""
    return CalendarEvent(
        start=pytz.utc.localize(job.due_date).date(),
        end=pytz.utc.localize(job.due_date).date(),
        summary=job.title,
        uid=job.scheduled_job_id,
    )


class ChildJobCalendar(CalendarEntity, RoosterChildEntity):
    """A job calendar for a child"""

    def __init__(
        self, account: ChildAccount, session: RoosterMoney, entity_id: str
    ) -> None:
        super().__init__(account=account, session=session, entity_id=entity_id)

    @property
    def name(self) -> str | UndefinedType | None:
        return "Jobs"

    @property
    def event(self) -> CalendarEvent | None:
        if len(self._child.jobs) == 0:
            return None
        else:
            return build_calendar_event(self._child.jobs[0])

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Returns all calendar events between a start and end date"""
        # CURRENTLY ONLY SUPPORTS THE CURRENT WEEK
        events: list[CalendarEvent] = []
        for job in self._child.jobs:
            _LOGGER.debug(
                "Convert Job %s into CalendarEvent type", job.scheduled_job_id
            )
            event: CalendarEvent = build_calendar_event(job)
            events.append(event)

        return events

    async def async_set_job_completed(self, job_id: int) -> None:
        """Sets a job as complete."""
        return None
