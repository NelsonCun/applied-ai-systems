from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.query import (
    QueryResolveRequest,
    QueryResolveResponse,
)
from app.services.query_service import QueryService


router = APIRouter(
    prefix="/queries",
    tags=["Consultas del bot"],
)


@router.post(
    "/resolve",
    response_model=QueryResolveResponse,
)
def resolve_query(
    data: QueryResolveRequest,
    database: Session = Depends(get_db),
) -> QueryResolveResponse:
    return QueryService.resolve(
        database=database,
        data=data,
    )
