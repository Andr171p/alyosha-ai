from pydantic import NonNegativeInt

from modules.shared_kernel.domain import AggregateRoot


class Catalog(AggregateRoot):
    items_count: NonNegativeInt
