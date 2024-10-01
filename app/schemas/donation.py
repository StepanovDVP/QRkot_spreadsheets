from datetime import datetime
from typing import Optional

from pydantic import BaseModel, conint

from app.constants import FULL_AMOUNT_MIN_VALUE


class DonationBase(BaseModel):
    full_amount: conint(gt=FULL_AMOUNT_MIN_VALUE)
    comment: Optional[str]


class DonationCreate(DonationBase):
    pass


class DonationDB(DonationBase):
    id: int
    create_date: datetime

    class Config:
        orm_mode = True


class DonationSuperUserDB(DonationDB):
    user_id: int
    invested_amount: int
    fully_invested: bool
    close_date: Optional[datetime]
