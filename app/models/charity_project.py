from sqlalchemy import Column, String, Text

from app.constants import NAME_MAX_LENGTH
from app.models.base_model import BaseProjectModel


class CharityProject(BaseProjectModel):
    name = Column(String(NAME_MAX_LENGTH), unique=True, nullable=False)
    description = Column(Text, nullable=False)

    def __repr__(self):
        return (
            f'id={self.id} {self.name}'
        )
