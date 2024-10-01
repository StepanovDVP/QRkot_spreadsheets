from datetime import datetime
from typing import TypeVar

ModelBase = TypeVar('ModelBase')


def calculate_investment_amount(
        source: ModelBase, target: ModelBase
) -> int:
    """Вычислить сумму, которая может быть инвестирована."""
    required_amount = target.full_amount - target.invested_amount
    available_amount = source.full_amount - source.invested_amount
    return min(required_amount, available_amount)


def update_investment_status(
        obj: ModelBase, invested_amount: int
):
    """Обновить статус объекта при полном инвестировании."""

    obj.invested_amount += invested_amount
    if obj.invested_amount == obj.full_amount:
        obj.fully_invested = True
        obj.close_date = datetime.now()


def invest_processing(
        source: ModelBase,
        targets: list[ModelBase]
) -> list[ModelBase]:
    """Распределить средства по принципу First In, First Out (FIFO)."""

    updated_objects = []

    for target in targets:

        if source.fully_invested:
            break

        invest_amount = calculate_investment_amount(source, target)

        update_investment_status(source, invest_amount)
        update_investment_status(target, invest_amount)

        updated_objects.extend([source, target])

    return updated_objects
