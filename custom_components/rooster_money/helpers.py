"""rooster_money helpers."""

import json
from pyroostermoney.child.jobs import Job, JobScheduleTypes, JobState, JobTime
from datetime import datetime


class JobEncoder(json.JSONEncoder):
    """JSON Encoder for Job types."""

    def default(self, o):
        if isinstance(o, Job):
            return {
                "description": o.description,
                "currency": o.currency,
                "allowance_period_id": o.allowance_period_id,
                "due_any_day": o.due_any_day,
                "due_date": o.due_date,
                "expiry_processed": o.expiry_processed,
                "final_reward_amount": o.final_reward_amount,
                "image_url": o.image_url,
                "locked": o.locked,
                "reopened": o.reopened,
                "reward_amount": o.reward_amount,
                "title": o.title,
                "type": o.type,
                "schedule_type": o.schedule_type,
                "scheduled_job_id": o.scheduled_job_id,
                "state": o.state,
                "weekdays": o.weekdays,
            }
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, JobScheduleTypes):
            return str(o)
        if isinstance(o, JobState):
            return str(o)
        if isinstance(o, JobTime):
            return str(o)
        try:
            return json.JSONEncoder.default(self, o)
        except:
            raise TypeError("Unexpected type", o.__class__.__name__)
