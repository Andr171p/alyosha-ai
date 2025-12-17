from uuid import UUID

from pydantic import Field

from modules.shared_kernel.domain import AggregateRoot, Entity

from .value_objects import ModelConfiguration


class ModelsRegistry(AggregateRoot):
    """Заготовленные и пред-настроенные модели"""


class Assistant(Entity):
    workspace_id: UUID
    name: str
    system_prompt: str
    model_configuration: ModelConfiguration
    connected_agents: list[UUID] = Field(default_factory=list)

    def configure_model(self, configuration: ModelConfiguration) -> None:
        self.model_configuration = configuration

    def connect_agent(self) -> ...: ...
