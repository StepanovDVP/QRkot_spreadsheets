from datetime import datetime

from sqlalchemy import (
    Column, Integer, CheckConstraint, Boolean, DateTime
)

from app.constants import INVESTED_AMOUNT_INIT
from app.core.db import Base


class BaseProjectModel(Base):
    __abstract__ = True

    full_amount = Column(Integer, nullable=False)
    invested_amount = Column(Integer, default=INVESTED_AMOUNT_INIT)
    fully_invested = Column(Boolean, default=False)
    create_date = Column(DateTime, default=datetime.now)
    close_date = Column(DateTime)

    __table_args__ = (
        CheckConstraint(
            'full_amount > 0',
            name='check_full_amount_positive'),
    )
