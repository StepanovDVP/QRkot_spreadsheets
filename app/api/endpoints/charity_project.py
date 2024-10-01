from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_full_amount, check_name_duplicate,
    check_project_before_edit
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud import project_crud, donation_crud
from app.schemas.charity_project import (
    CharityProjectCreate, CharityProjectDB, CharityProjectUpdate
)
from app.services.invest_processing import invest_processing

router = APIRouter()


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_new_project(
        project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Создать новый благотворительный проект.

    Функция проверяет уникальность имени проекта,
    создает новый проект в базе данных,
    а затем распределяет имеющиеся пожертвования по принципу FIFO.

    Доступно только для суперпользователей.
    """

    await check_name_duplicate(project.name, session)
    new_project = await project_crud.create(project, session, commit=False)
    donations = await donation_crud.get_objects_for_invest_processing(
        session=session
    )

    updated_objects = invest_processing(new_project, donations)

    for obj in updated_objects:
        session.add(obj)

    await session.commit()
    await session.refresh(new_project)

    return new_project


@router.patch(
    '/{project_id}',
    response_model_exclude_none=True,
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)])
async def update_project(
        project_id: int,
        obj_in: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Обновить существующий проект, доступно только для суперюзеров.

    В рамках обновления можно изменить:
    - Название проекта (`name`)
    - Описание проекта (`description`)
    - Требуемую сумму для проекта (`full_amount`),
      но она не может быть меньше уже внесённой суммы (`invested_amount`).

    Через API невозможно:
    - Изменить размер уже внесённых средств в проект.
    - Изменить даты создания и закрытия проекта.
    """

    project = await check_project_before_edit(project_id, session)

    if obj_in.name is not None:
        await check_name_duplicate(obj_in.name, session)

    if obj_in.full_amount is not None:
        check_full_amount(
            current_invested_amount=project.invested_amount,
            new_full_amount=obj_in.full_amount
        )
    project = await project_crud.update(
        db_obj=project, obj_in=obj_in, session=session
    )

    return project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def delete_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Удалить проект, доступно только для суперюзеров.

    Через API невозможно:
    - Удалить проекты, в которые уже были внесены средства.
    - Удалить или модифицировать закрытые проекты.

    Если в проект уже инвестированы средства, его можно только закрыть.
    """

    project = await check_project_before_edit(project_id, session)

    if project.invested_amount > 0:
        raise HTTPException(
            status_code=400,
            detail='Нельзя удалить проект, '
                   'в который уже были инвестированы средства, '
                   'его можно только закрыть.'
        )
    project = await project_crud.remove(db_obj=project, session=session)

    return project


@router.get('/',
            response_model=list[CharityProjectDB],
            response_model_exclude_none=True, )
async def get_project(
        session: AsyncSession = Depends(get_async_session)
):
    """Получить все проекты."""

    projects = await project_crud.get_multi(session)
    return projects
