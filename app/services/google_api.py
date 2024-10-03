from datetime import datetime
import copy
from string import ascii_uppercase

from aiogoogle import Aiogoogle

from app.core.config import settings
from app.constants import (
    SECONDS_OF_ONE_DAY, SECONDS_OF_HOUR,
    MINUTES_OF_HOUR, FORMAT, MAX_ROWS, MAX_COLUMNS,
    SPREADSHEET_URL
)
from app.exceptions import (
    MaxColumnsExceededError, MaxRowsExceededError
)

BASE_TABLE_VALUES = [
    ['Отчёт от', ''],
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание']
]

SPREADSHEET_BODY_TEMPLATE = {
    'properties': {'title': '', 'locale': 'ru_RU'},
    'sheets': [
        {'properties': {
            'sheetType': 'GRID',
            'sheetId': 0,
            'title': 'Лист1',
            'gridProperties':
                {'rowCount': MAX_ROWS,
                 'columnCount': MAX_COLUMNS}
        }
        }
    ]
}

PERMISSIONS_BODY = {
    'type': 'user',
    'role': 'writer',
    'emailAddress': settings.email
}


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
    service = await wrapper_services.discover('sheets', 'v4')
    table_values = copy.deepcopy(BASE_TABLE_VALUES)
    table_values[0][1] = now_date_time

    for project in closed_projects:
        new_row = [
            str(project['name']),
            difference_days(project['duration_days']),
            str(project['description'])
        ]
        table_values.append(new_row)

    total_rows = len(table_values)

    if total_rows > MAX_ROWS:
        raise MaxRowsExceededError(
            f"Превышено максимальное количество строк "
            f"({MAX_ROWS}). Текущие строки: {total_rows}."
        )

    for row in table_values:
        if len(row) > MAX_COLUMNS:
            raise MaxColumnsExceededError(
                f"Превышено максимальное количество столбцов "
                f"({MAX_COLUMNS}) в строке: {row}."
            )

    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }

    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=f'A1:{ascii_uppercase[MAX_COLUMNS - 1]}{MAX_ROWS}',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )


async def spreadsheets_create(wrapper_services: Aiogoogle) -> tuple:
    """Создать  документ с таблицами."""

    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheet_body = copy.deepcopy(SPREADSHEET_BODY_TEMPLATE)
    spreadsheet_body['properties']['title'] = f'Отчёт на {now_date_time}'
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    spreadsheet_id = response['spreadsheetId']
    spreadsheet_url = SPREADSHEET_URL + spreadsheet_id

    return spreadsheet_id, spreadsheet_url


async def set_user_permissions(
        spreadsheet_id: str,
        wrapper_services: Aiogoogle
) -> None:
    """Предоставить права доступа к созданному документу."""

    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=PERMISSIONS_BODY,
            fields="id"
        ))
