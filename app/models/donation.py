from sqlalchemy import Column, Text, Integer, ForeignKey

from app.models.base_model import BaseProjectModel


class Donation(BaseProjectModel):
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text)

    def __repr__(self):
        return (
            f' {self.id} всего: {self.full_amount}  '
            f'потрачено: {self.invested_amount}'
        )
