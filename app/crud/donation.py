from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Donation, User
from app.schemas.donation import DonationCreate


class CRUDDonation(
    CRUDBase[
        Donation,
        DonationCreate,
        None]
):
    async def get_by_user(self, session: AsyncSession, user: User):
        """Получить донаты пользовователя."""
        query = select(Donation).where(
            Donation.user_id == user.id
        )
        all_donations = await session.execute(query)
        return all_donations.scalars().all()


donation_crud = CRUDDonation(Donation)
