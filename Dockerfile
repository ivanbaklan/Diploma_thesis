# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем зависимости не python
RUN apt-get update && apt-get install -y make gcc htop ffmpeg

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY ./pyproject.toml /app/pyproject.toml
COPY ./uv.lock /app/uv.lock
COPY ./Makefile /app/Makefile
COPY ./VERSION /app/VERSION
COPY ./contextly /app/contextly

# Устанавливаем зависимости
RUN make install

# Открываем порт 8080
EXPOSE 8080

# Команда для запуска приложения
CMD [".venv/bin/python", "-m", "uvicorn", "contextly.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]