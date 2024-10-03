from sqlalchemy.ext.asyncio import AsyncSession

from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends, HTTPException

from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser
from app.crud.charity_project import project_crud
from app.services.google_api import (
    spreadsheets_create, set_user_permissions, spreadsheets_update_value
)
from app.exceptions import (
    MaxColumnsExceededError, MaxRowsExceededError
)

router = APIRouter()


@router.post(
    '/',
    response_model=str,
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
    closed_projects = await (
        project_crud.get_projects_by_completion_rate(session)
    )
    spreadsheet_id, spreadsheet_url = await spreadsheets_create(
        wrapper_services
    )
    await set_user_permissions(spreadsheet_id, wrapper_services)
    try:
        await spreadsheets_update_value(
            spreadsheet_id, closed_projects, wrapper_services
        )
    except (MaxColumnsExceededError, MaxRowsExceededError) as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при работе с Google Sheets: {str(e)}"
        )

    return spreadsheet_url
