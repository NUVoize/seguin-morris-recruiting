"""Schemas for agent runs - what the UI polls to render the live timeline."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import AgentRunStatus, AgentType


class AgentStepRead(BaseModel):
    """One log line emitted by an agent."""

    ts: str
    icon: str
    message: str
    detail: dict[str, Any] | None = None


class AgentRunOutput(BaseModel):
    """Parsed agent_runs.output_summary JSON blob."""

    agent_type: str
    display_name: str = ""
    icon: str = "*"
    status: str = "pending"
    steps: list[AgentStepRead] = Field(default_factory=list)
    counts: dict[str, int] = Field(default_factory=dict)


class AgentRunRead(BaseModel):
    """One row from the agent_runs table, with parsed output_summary.

    The DB column is named `output_summary` (a JSON-encoded string); we expose it
    to the API as `output` (a structured object) after parsing.
    """

    id: uuid.UUID
    campaign_id: uuid.UUID | None
    agent_type: AgentType
    status: AgentRunStatus
    started_at: datetime | None
    completed_at: datetime | None
    output: AgentRunOutput | None = None
    error_log: dict[str, Any] | None = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def _flatten_orm(cls, data: Any) -> Any:
        """Read the SQLAlchemy AgentRun model: map output_summary string -> parsed output."""
        # If we already got a dict (e.g. from another schema), pass through unchanged
        # except for ensuring `output` is parsed.
        if isinstance(data, dict):
            raw = data.get("output", data.get("output_summary"))
            if isinstance(raw, str):
                try:
                    data["output"] = json.loads(raw)
                except (json.JSONDecodeError, TypeError):
                    data["output"] = None
            return data

        # SQLAlchemy ORM instance - read attributes and pre-parse the JSON column
        raw = getattr(data, "output_summary", None)
        parsed: dict | None = None
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                parsed = None

        return {
            "id": data.id,
            "campaign_id": data.campaign_id,
            "agent_type": data.agent_type,
            "status": data.status,
            "started_at": data.started_at,
            "completed_at": data.completed_at,
            "output": parsed,
            "error_log": getattr(data, "error_log", None),
        }


class TriggerAgentRunResponse(BaseModel):
    """Returned immediately when a run is kicked off in the background."""

    started_at: datetime
    campaign_id: uuid.UUID | None
    agents: list[str]
    message: str