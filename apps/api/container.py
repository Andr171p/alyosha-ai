from typing import Final

from dishka import AsyncContainer, make_async_container

from modules.workspaces.infrastructure.container import AdminProvider
from modules.iam.infrastructure.container import IAMProvider
from modules.shared_kernel.insrastructure.container import SharedKernelProvider

container: Final[AsyncContainer] = make_async_container(
    SharedKernelProvider(), IAMProvider(), AdminProvider(),
)
