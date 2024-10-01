from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, conint, constr, validator

from app.constants import (
    FULL_AMOUNT_MIN_VALUE, MIN_LENGTH, NAME_MAX_LENGTH
)


class CharityProjectBase(BaseModel):
    name: Optional[constr(max_length=NAME_MAX_LENGTH)]
    description: Optional[str]
    full_amount: Optional[conint(gt=FULL_AMOUNT_MIN_VALUE)]

    class Config:
        extra = Extra.forbid
        min_anystr_length = MIN_LENGTH


class CharityProjectUpdate(CharityProjectBase):
    @validator('name', 'description', pre=True)
    def fields_must_not_be_empty(cls, value):
        if value is not None and not value.strip():
            raise ValueError('Поля "name" и "description" '
                             'не должны быть пустыми или '
                             'состоять только из пробелов.')
        return value


class CharityProjectCreate(CharityProjectUpdate):
    name: constr(max_length=NAME_MAX_LENGTH)
    description: str
    full_amount: conint(gt=FULL_AMOUNT_MIN_VALUE)


class CharityProjectDB(CharityProjectCreate):
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime]

    class Config:
        orm_mode = True
