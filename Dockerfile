
FROM python:3.12.9 AS prod

# Устанавливаем необходимые зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*


# Создаем директории для проекта
WORKDIR /KURS_BACK/

# Копируем pyproject.toml и poetry.lock
COPY requirements.txt /KURS_BACK/

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Очищаем кэш
RUN apt-get purge -y && rm -rf /var/lib/apt/lists/*

# Копируем приложение
COPY . /KURS_BACK/