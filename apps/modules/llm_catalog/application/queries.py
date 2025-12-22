from modules.shared_kernel.application import Pagination
from modules.shared_kernel.domain import Query

from .dto import LLMFilters


class SearchLLMsInCatalogQuery(Query):
    """Запрос для поиска LLM в каталоге"""

    filters: LLMFilters
    pagination: Pagination
