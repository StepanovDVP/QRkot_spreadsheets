from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import project_crud
from app.models import CharityProject


async def check_name_duplicate(
        project_name: str,
        session: AsyncSession,
) -> None:
    """Проверить на дубликат по полю name."""

    room_id = await project_crud.get_project_id_by_name(project_name, session)
    if room_id is not None:
        raise HTTPException(
            status_code=400,
            detail='Проект с таким именем уже существует!',
        )


async def check_project_before_edit(
        project_id: int,
        session: AsyncSession,
) -> CharityProject:
    """Проверить элемент при обновлении."""

    project = await project_crud.get(project_id, session)

    if not project:
        raise HTTPException(
            status_code=404,
            detail='Проект не найден!'
        )
    if project.fully_invested:
        raise HTTPException(
            status_code=400,
            detail='Проект закрыт!'
        )

    return project


def check_full_amount(
        current_invested_amount: int,
        new_full_amount: int,
) -> None:
    """Проверить, что новая сумма не меньше инвестируемой."""

    if new_full_amount < current_invested_amount:
        raise HTTPException(
            status_code=422,
            detail='Новая сумма не может быть '
                   'меньше инвестированной суммы.'
        )
