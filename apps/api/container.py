from typing import Final

from dishka import AsyncContainer, make_async_container

from modules.iam.infrastructure.container import IAMProvider
from modules.models_registry.infrastructure.container import ModelsRegistryProvider
from modules.shared_kernel.insrastructure.container import SharedKernelProvider
from modules.workspaces.infrastructure.container import AdminProvider

container: Final[AsyncContainer] = make_async_container(
    SharedKernelProvider(), IAMProvider(), ModelsRegistryProvider(), AdminProvider(),
)
