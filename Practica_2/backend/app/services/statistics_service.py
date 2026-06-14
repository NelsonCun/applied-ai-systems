from sqlalchemy.orm import Session

from app.repositories.statistics_repository import (
    StatisticsRepository,
)
from app.schemas.statistics import (
    CategoryStatisticsItem,
    StatisticsSummaryResponse,
    TopQueryItem,
    TopQuestionItem,
)


class StatisticsService:
    @staticmethod
    def get_summary(
        database: Session,
    ) -> StatisticsSummaryResponse:
        return StatisticsSummaryResponse(
            **StatisticsRepository.get_summary(
                database=database
            )
        )

    @staticmethod
    def get_top_questions(
        database: Session,
        limit: int,
    ) -> list[TopQuestionItem]:
        return [
            TopQuestionItem(**item)
            for item in (
                StatisticsRepository.get_top_questions(
                    database=database,
                    limit=limit,
                )
            )
        ]

    @staticmethod
    def get_top_queries(
        database: Session,
        limit: int,
    ) -> list[TopQueryItem]:
        return [
            TopQueryItem(**item)
            for item in (
                StatisticsRepository.get_top_queries(
                    database=database,
                    limit=limit,
                )
            )
        ]

    @staticmethod
    def get_by_category(
        database: Session,
    ) -> list[CategoryStatisticsItem]:
        return [
            CategoryStatisticsItem(**item)
            for item in (
                StatisticsRepository
                .get_statistics_by_category(
                    database=database
                )
            )
        ]
