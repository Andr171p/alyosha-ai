from pydantic import HttpUrl
from sqlalchemy import desc, select
from sqlalchemy.exc import SQLAlchemyError

from modules.shared_kernel.application import Pagination
from modules.shared_kernel.application.exceptions import ReadingError
from modules.shared_kernel.insrastructure.database import DataMapper, SQLAlchemyRepository

from ...application import CatalogRepository, LLMFilters
from ...domain import CardStatus, LLMCard, LLMCategory
from .models import LLMCardModel, UserFeedbackModel


class LLMCardDataMapper(DataMapper[LLMCard, LLMCardModel]):
    @classmethod
    def model_to_entity(cls, model: LLMCardModel) -> LLMCard:
        return LLMCard(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            status=CardStatus(model.status),
            category=LLMCategory(model.category),
            name=model.name,
            slug=model.slug,
            family=model.family,
            description=model.description,
            tags=model.tags,
            provider_name=model.provider_name,
            source_url=HttpUrl(model.source_url),
            capabilities=model.capabilities,
            performance_characteristics=model.performance_characteristics,
            business_presentation=model.business_presentation,
            hardware_requirements=model.hardware_requirements,
            billing_tier=model.billing_tier,
        )

    @classmethod
    def entity_to_model(cls, entity: LLMCard) -> LLMCardModel:
        return LLMCardModel(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            status=entity.status.value(),
            category=entity.category.value(),
            name=entity.name,
            slug=entity.slug,
            family=entity.family,
            description=entity.description,
            tags=entity.tags,
            provider_name=entity.provider_name,
            source_url=str(entity.source_url),
            capabilities=entity.capabilities,
            performance_characteristics=entity.performance_characteristics,
            business_presentation=entity.business_presentation,
            hardware_requirements=entity.hardware_requirements,
            billing_tier=entity.billing_tier,
        )


class SQLAlchemyCatalogRepository(SQLAlchemyRepository[LLMCard, LLMCardModel], CatalogRepository):
    entity = LLMCard
    model = LLMCardModel
    data_mapper = LLMCardDataMapper

    async def get_most_popular(self, pagination: Pagination) -> list[LLMCard]:
        try:
            stmt = (
                select(self.model)
                .join(UserFeedbackModel, self.model.id == UserFeedbackModel.llm_card_id)
                .order_by(desc(UserFeedbackModel.rating))
                .offset(pagination.offset)
                .limit(pagination.limit)
            )
            results = await self.session.execute(stmt)
            models = results.scalars().all()
            return [
                self.data_mapper.model_to_entity(model) for model in models
            ]
        except SQLAlchemyError as e:
            raise ReadingError(
                entity_name=self.entity.__class__.__name__,
                entity_id="*",
                details={**pagination.model_dump()},
                original_error=e
            ) from e

    async def search_by_filters(
            self, filters: LLMFilters, pagination: Pagination
    ) -> list[LLMCard]:
        try:
            return ...
        except SQLAlchemyError as e:
            raise ReadingError(
                entity_name=self.entity.__class__.__name__,
                entity_id="*",
                details={**filters.model_dump(), **pagination.model_dump()},
                original_error=e
            ) from e
