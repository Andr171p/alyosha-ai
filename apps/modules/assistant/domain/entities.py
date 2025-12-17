from uuid import UUID

from pydantic import Field

from modules.shared_kernel.domain import Entity

from .value_objects import ModelConfiguration


class Assistant(Entity):
    workspace_id: UUID
    name: str
    system_prompt: str
    model_configuration: ModelConfiguration
    connected_agents: list[UUID] = Field(default_factory=list)
