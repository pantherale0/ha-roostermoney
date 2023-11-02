"""Rooster Money todo list."""

from __future__ import annotations
from collections.abc import Mapping
from typing import Any
import json


from homeassistant.components.todo import (
    TodoItem,
    TodoItemStatus,
    TodoListEntity,
    TodoListEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from pyroostermoney.child.jobs import Job, JobState, JobActions

from .const import DOMAIN
from .rooster_base import RoosterChildEntity
from .helpers import JobEncoder

async def async_setup_entry(
        hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Init platform."""
    entities = []
    for child in hass.data[DOMAIN][entry.entry_id].rooster.children:
        entities.append(
            RoosterJobsTodoEntity(
                hass.data[DOMAIN][entry.entry_id],
                None,
                child.user_id,
                entity_id="jobs_todo"
            )
        )
    async_add_entities(entities, True)

def _convert_job_status_to_todo(state: JobState) -> TodoItemStatus:
    if state is JobState.APPROVED:
        return TodoItemStatus.COMPLETED
    if state is JobState.SKIPPED:
        return TodoItemStatus.COMPLETED
    if state is JobState.PAUSED:
        return TodoItemStatus.COMPLETED
    if state is JobState.AWAITING_APPROVAL:
        return TodoItemStatus.COMPLETED
    return TodoItemStatus.NEEDS_ACTION



def _convert_jobs_to_todo(jobs: list[Job]) -> list[TodoItem]:
    """Convert a list of jobs to todo list items."""
    items = []
    for job in jobs:
        items.append(
            TodoItem(
                job.title,
                job.scheduled_job_id,
                _convert_job_status_to_todo(job.state)
            )
        )
    return items


class RoosterJobsTodoEntity(RoosterChildEntity, TodoListEntity):
    """Job todo list entity."""

    def _get_job(self, job_id) -> Job:
        """Return a single job from the cache."""
        return [x for x in self._child.jobs if x.scheduled_job_id is job_id][0]

    @property
    def supported_features(self) -> int | None:
        """Return supported feature."""
        return (
            TodoListEntityFeature.UPDATE_TODO_ITEM
        )

    @property
    def name(self) -> str:
        """Return entity name."""
        return f"{self._child.first_name} Jobs This Week"

    @property
    def unique_id(self):
        """Return entity unique ID."""
        return f"{self._child.first_name}_job_todolist"

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return an array of jobs."""
        return {
            "jobs": json.dumps(self._child.jobs, cls=JobEncoder),
            "count": len(self._child.jobs),
        }

    @property
    def todo_items(self) -> list[TodoItem] | None:
        """Return items."""
        return _convert_jobs_to_todo(self._child.jobs)

    async def async_update_todo_item(self, item: TodoItem) -> None:
        """Update the todo item state."""
        if item.status is TodoItemStatus.COMPLETED:
            await self._get_job(item.uid).job_action(
                action=JobActions.APPROVE,
                message="Approved via Home Assistant todos"
            )
        else:
            raise ValueError("Job %s is already complete for user %s.", item.uid, self._child_id)
