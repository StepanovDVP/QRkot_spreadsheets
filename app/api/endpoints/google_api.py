from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession

from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends

from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser
from app.crud.charity_project import project_crud
from app.services.google_api import (
    spreadsheets_create, set_user_permissions, spreadsheets_update_value
)

router = APIRouter()


@router.post(
    '/',
    response_model=list[dict[str, Union[str, float]]],
    dependencies=[Depends(current_superuser)],
)
async def get_report(
        session: AsyncSession = Depends(get_async_session),
        wrapper_services: Aiogoogle = Depends(get_service)
):
    """
    Получить отчет о закрытых проектах
    отсортированные по скорости сбора средств.
    Сформировать в гугл-таблице.
    Только для суперюзеров.
    """
    closed_projects = await (project_crud
                             .get_projects_by_completion_rate(session))
    spreadsheet_id = await spreadsheets_create(wrapper_services)
    await set_user_permissions(spreadsheet_id, wrapper_services)
    await spreadsheets_update_value(
        spreadsheet_id, closed_projects, wrapper_services
    )
    return closed_projects
