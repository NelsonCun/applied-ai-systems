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
from app.schemas.question import (
    QuestionCreate,
    QuestionResponse,
    QuestionUpdate,
)
from app.services.question_service import QuestionService


router = APIRouter(
    prefix="/questions",
    tags=["Preguntas"],
)


@router.get(
    "",
    response_model=list[QuestionResponse],
)
def list_questions(
    search: str | None = Query(
        default=None,
        max_length=100,
    ),
    category_id: int | None = Query(
        default=None,
        gt=0,
    ),
    is_active: bool | None = Query(default=None),
    database: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    del current_user

    return QuestionService.list_all(
        database=database,
        search=search,
        category_id=category_id,
        is_active=is_active,
    )


@router.post(
    "",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_question(
    data: QuestionCreate,
    database: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    del current_user

    return QuestionService.create(
        database=database,
        data=data,
    )


@router.get(
    "/{question_id}",
    response_model=QuestionResponse,
)
def get_question(
    question_id: int,
    database: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    del current_user

    return QuestionService.get_by_id(
        database=database,
        question_id=question_id,
    )


@router.put(
    "/{question_id}",
    response_model=QuestionResponse,
)
def update_question(
    question_id: int,
    data: QuestionUpdate,
    database: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    del current_user

    return QuestionService.update(
        database=database,
        question_id=question_id,
        data=data,
    )


@router.delete(
    "/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_question(
    question_id: int,
    database: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
) -> Response:
    del current_user

    QuestionService.delete(
        database=database,
        question_id=question_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
