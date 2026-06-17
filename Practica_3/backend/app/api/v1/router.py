from fastapi import APIRouter

from app.api.v1.automations import router as automations_router
from app.api.v1.auth import router as auth_router
from app.api.v1.categories import router as categories_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.invoices import router as invoices_router
from app.api.v1.providers import router as providers_router
from app.api.v1.reports import router as reports_router


api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(automations_router)
api_router.include_router(categories_router)
api_router.include_router(dashboard_router)
api_router.include_router(providers_router)
api_router.include_router(invoices_router)
api_router.include_router(reports_router)
