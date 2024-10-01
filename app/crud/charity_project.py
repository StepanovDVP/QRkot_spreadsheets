from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject
from app.schemas.charity_project import (
    CharityProjectCreate, CharityProjectUpdate
)


class CRUDCharityProject(
    CRUDBase[
        CharityProject,
        CharityProjectCreate,
        CharityProjectUpdate
    ]
):

    async def get_project_id_by_name(
            self,
            project_name: str,
            session: AsyncSession,
    ) -> Optional[int]:
        """Получить проект по полю name."""
        db_project_id = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == project_name
            )
        )
        db_project_id = db_project_id.scalars().first()
        return db_project_id

    async def get_projects_by_completion_rate(
            self,
            session: AsyncSession
    ):
        """
        Получить закрытые проекты
        с временным расчетом по дате сбора средств.
        """
        query = select(
            CharityProject.name,
            (func.julianday(CharityProject.close_date) -
             func.julianday(CharityProject.create_date)
             ).label('duration_days'),
            CharityProject.description
        ).where(
            CharityProject.fully_invested.is_(True)
        ).order_by('duration_days')
        projects = await session.execute(query)
        projects = projects.all()
        return projects


project_crud = CRUDCharityProject(CharityProject)
