from fastapi import (
    APIRouter,
    Depends,
    Query,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_admin
from app.db.session import get_db
from app.models import AdminUser
from app.schemas.answer import (
    AnswerCreate,
    AnswerResponse,
    AnswerUpdate,
)
from app.services.answer_service import AnswerService


router = APIRouter(
    prefix="/answers",
    tags=["Respuestas"],
)


@router.get(
    "",
    response_model=list[AnswerResponse],
)
def list_answers(
    is_active: bool | None = Query(default=None),
    database: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    del current_user

    return AnswerService.list_all(
        database=database,
        is_active=is_active,
    )


@router.post(
    "",
    response_model=AnswerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_answer(
    data: AnswerCreate,
    database: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    del current_user

    return AnswerService.create(
        database=database,
        data=data,
    )


@router.get(
    "/{answer_id}",
    response_model=AnswerResponse,
)
def get_answer(
    answer_id: int,
    database: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    del current_user

    return AnswerService.get_by_id(
        database=database,
        answer_id=answer_id,
    )


@router.put(
    "/{answer_id}",
    response_model=AnswerResponse,
)
def update_answer(
    answer_id: int,
    data: AnswerUpdate,
    database: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    del current_user

    return AnswerService.update(
        database=database,
        answer_id=answer_id,
        data=data,
    )


@router.delete(
    "/{answer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_answer(
    answer_id: int,
    database: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
) -> Response:
    del current_user

    AnswerService.delete(
        database=database,
        answer_id=answer_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
