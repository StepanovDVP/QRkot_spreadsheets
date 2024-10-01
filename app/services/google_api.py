from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings
from app.constants import (
    SECONDS_OF_ONE_DAY, SECONDS_OF_HOUR,
    MINUTES_OF_HOUR, FORMAT
)


def difference_days(days_diff: float) -> str:
    """Привести к формату врменной отчет."""

    difference_in_days = days_diff
    days = int(difference_in_days)
    fractional_days = difference_in_days - days

    total_seconds = fractional_days * SECONDS_OF_ONE_DAY

    hours = int(total_seconds // SECONDS_OF_HOUR)
    total_seconds %= SECONDS_OF_HOUR

    minutes = int(total_seconds // MINUTES_OF_HOUR)
    seconds = float(total_seconds % MINUTES_OF_HOUR)
    day_word = "day" if days == 1 else "days"
    formatted_time_difference = (f"{days} {day_word}, "
                                 f"{hours:01}:{minutes:02}:{seconds:02.6f}")
    return formatted_time_difference


async def spreadsheets_update_value(
        spreadsheet_id: str,
        closed_projects: list,
        wrapper_services: Aiogoogle
) -> None:
    """Заполнить таблицу данными."""
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover(
        'sheets', 'v4'
    )
    table_values = [
        ['Отчёт от', now_date_time],
        ['Топ проектов по скорости закрытия'],
        ['Название проекта', 'Время сбора', 'Описание']
    ]
    for project in closed_projects:
        new_row = [
            str(project['name']),
            difference_days(project['duration_days']),
            str(project['description'])
        ]
        table_values.append(new_row)

    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range='A1:E30',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    """Создать  документ с таблицами."""

    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheet_body = {
        'properties': {'title': f'Отчёт на {now_date_time}',
                       'locale': 'ru_RU'},
        'sheets': [{'properties': {'sheetType': 'GRID',
                                   'sheetId': 0,
                                   'title': 'Лист1',
                                   'gridProperties': {'rowCount': 100,
                                                      'columnCount': 11}}}]
    }
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    spreadsheet_id = response['spreadsheetId']
    return spreadsheet_id
    ...


async def set_user_permissions(
        spreadsheet_id: str,
        wrapper_services: Aiogoogle
) -> None:
    """Предоставить права доступа к созданному документу."""
    permissions_body = {'type': 'user',
                        'role': 'writer',
                        'emailAddress': settings.email}
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=permissions_body,
            fields="id"
        ))
