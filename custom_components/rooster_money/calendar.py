"""Defines a CalendarEntity for Rooster Money job's"""

import logging
from dateutil import rrule as RR
from datetime import datetime, timezone, date, timedelta
from pyroostermoney import RoosterMoney

from pyroostermoney.child import ChildAccount, Job
from pyroostermoney.enum import JobTime, JobScheduleTypes, Weekdays
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
    for child in hass.data[DOMAIN][config_entry.entry_id].rooster.children:
        entities.append(
            ChildJobCalendar(
                coordinator=hass.data[DOMAIN][config_entry.entry_id],
                idx=None,
                child_id=child.user_id,
                entity_id="jobs",
            )
        )

    async_add_entities(entities, True)


def build_calendar_event(
    title: str, due_date: datetime, time_of_day: JobTime, id
) -> CalendarEvent:
    """Converts a job to a calendar event."""
    due_date = due_date.replace(tzinfo=None)
    event = CalendarEvent(
        start=pytz.utc.localize(due_date).date(),
        end=pytz.utc.localize(due_date).date(),
        summary=title,
        uid=id,
    )
    if time_of_day is JobTime.MORNING:
        event.start = pytz.utc.localize(due_date).replace(hour=5, minute=0)
        event.end = pytz.utc.localize(due_date).replace(hour=12, minute=0)
    if time_of_day is JobTime.AFTERNOON:
        event.start = pytz.utc.localize(due_date).replace(hour=12, minute=0)
        event.end = pytz.utc.localize(due_date).replace(hour=17, minute=0)
    if time_of_day is JobTime.EVENING:
        event.start = pytz.utc.localize(due_date).replace(hour=17, minute=0)
        event.end = pytz.utc.localize(due_date).replace(hour=21, minute=0)
    return event


class ChildJobCalendar(CalendarEntity, RoosterChildEntity):
    """A job calendar for a child"""

    @property
    def name(self) -> str | UndefinedType | None:
        return "Jobs"

    @property
    def event(self) -> CalendarEvent | None:
        if len(self._child.jobs) == 0:
            return None
        # get next job
        job_id = self._child.jobs[0].master_job_id
        jobs = list(
            filter(
                lambda job: job.master_job_id is job_id,
                self.coordinator.rooster.master_job_list,
            )
        )
        if len(jobs) == 0:
            return None
        return build_calendar_event(
            title=jobs[0].title,
            due_date=self._child.jobs[0].due_date,
            time_of_day=jobs[0].time_of_day,
            id=self._child.jobs[0].allowance_period_id,
        )

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime = datetime.today(),
        end_date: datetime = datetime.today(),
    ) -> list[CalendarEvent]:
        """Returns all calendar events between a start and end date"""
        # add 2 weeks of padding.
        job_start = start_date - timedelta(weeks=2)
        job_end = end_date + timedelta(weeks=2)
        events: list[CalendarEvent] = []
        for job in self.coordinator.rooster.master_jobs.get_child_master_job_list(
            self._child
        ):
            _LOGGER.debug("Convert Job %s into CalendarEvent type", job.master_job_id)
            # need to flatten the event(s)
            # we also ignore anytime events and unknown events as these have no set cycle
            if job.schedule_type is JobScheduleTypes.REPEATING:
                for weekday in job.weekdays:
                    # Create an event for each weekday
                    recurrance_range = RR.rrule(
                        RR.WEEKLY,
                        byweekday=int(weekday),
                        dtstart=job_start,
                        until=job_end,
                    )
                    for recurrance in recurrance_range:
                        events.append(
                            build_calendar_event(
                                title=job.title,
                                due_date=recurrance,
                                time_of_day=job.time_of_day,
                                id=job.master_job_id,
                            )
                        )
        return events

    async def async_set_job_completed(self, job_id: int) -> None:
        """Sets a job as complete."""
        return None
