# Проект: приложение QRKot

## Описание

Проект представляет фонд, который занимается сбором пожертвований
для различных целевых проектов, связанных с поддержкой кошачьей популяции.
Основные направления включают:

- Обеспечение медицинской помощи нуждающимся кошкам.
- Обустройство кошачьей колонии в подвалах и других местах.
- Закупка корма для оставшихся без попечения животных

## Стек технологий

- **Язык программирования**: Python
- **Веб-фреймворк**: Fastapi
- **База данных**: SQLite (или другая база данных по вашему выбору)
- **ORM**: SQLAlchemy
- **Формы и валидация**: Pydantic
- **Миграции базы данных**: Alembic

## Инструкция по установке и запуску

Клонировать репозиторий и перейти в него в командной строке:

```bash
git clone https://github.com/StepanovDVP/cat_charity_fund.git
```

```
cd cat_charity_fund
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/scripts/activate
    ```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

### Настройка конфигурации

Создайте файл .env и укажите необходимые параметры:

```
DATABASE_URI=sqlite+aiosqlite:///./fastapi.db (или другая база данных по вашему выбору)
SECRET=my_secret_key (установите ключ для шифрования поролей)
```

### Инициализация базы данных и миграции

Если база данных еще не создана, выполните инициализацию:

```
alembic init --template async alembic 
```

Откройте конфигурационный файл env.py:

```
cd alembic/env.py
```

В файле env.py импортируйте необходимые модули и компоненты:

```python
import os
from dotenv import load_dotenv
from app.core.base import Base

load_dotenv('.env')
config.set_main_option('sqlalchemy.url', os.environ['DATABASE_URL'])

target_metadata = Base.metadata
```

Затем создайте миграции и примените их:

```
alembic revision --autogenerate -m "First migration" 
alembic upgrade head 
```

### Запуск приложения

После настройки приложения его можно запустить:

```
app.main:app --reload
```

Приложение будет доступно по адресу: http://127.0.0.1:8000

## Тестирование API

Вы можете протестировать API с помощью Swagger,
описание доступных endpoints и  документацию можно посмотреть по ссылке:

```
http://127.0.0.1:8000/docs
```

## Авторы и техническое задание

- **Техническое задание**: [Yandex.Practicum](https://practicum.yandex.ru/)
- **Разработчик**: Степанов Дмитрий
    - GitHub: [StepanovDVP](https://github.com/StepanovDVP)
    - DockerHub: [DmitryStepanov24](https://hub.docker.com/u/DmitryStepanov24)

