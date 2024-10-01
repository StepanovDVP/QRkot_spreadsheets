from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud import donation_crud, project_crud
from app.models import User
from app.schemas.donation import (
    DonationCreate, DonationDB, DonationSuperUserDB
)
from app.services.invest_processing import invest_processing

router = APIRouter()


@router.post(
    '/',
    response_model=DonationDB,
    response_model_exclude={
        'user_id', 'invested_amount',
        'fully_invested', 'close_date'}
)
async def create_new_donation(
        donation: DonationCreate,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user)
):
    """
    Создать новое пожертвование.

    Функция принимает данные о пожертвовании
    от текущего авторизованного пользователя,
    создает запись в базе данных и распределяет пожертвование
    по проектам, требующим финансирования.

    Доступно только для авторизованных пользователей.
    """
    new_donation = await donation_crud.create(
        obj_in=donation, session=session, user=user, commit=False
    )

    projects = await project_crud.get_objects_for_invest_processing(
        session=session
    )
    updated_objects = invest_processing(new_donation, projects)

    for obj in updated_objects:
        session.add(obj)

    await session.commit()
    await session.refresh(new_donation)

    return new_donation


@router.get('/',
            response_model=list[DonationSuperUserDB],
            response_model_exclude_none=True,
            dependencies=[Depends(current_superuser)])
async def get_donations(
        session: AsyncSession = Depends(get_async_session)
):
    """
    Получить список всех пожертвований.

    Возвращает полную информацию обо всех пожертвованиях, включая:
    - ID пользователя, сделавшего пожертвование (`user_id`)
    - Сумма, уже проинвестированная (`invested_amount`)
    - Статус завершённости инвестирования (`fully_invested`)
    - Дата закрытия пожертвования (`close_date`)

    Эта информация доступна только для суперпользователей.
    """
    donations = await donation_crud.get_multi(session)
    return donations


@router.get(
    '/my',
    response_model=list[DonationDB],
)
async def get_my_donations(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user)
):
    """Получить список всех пожертвований текущего пользователя."""

    my_donations = await donation_crud.get_by_user(session=session, user=user)
    return my_donations
