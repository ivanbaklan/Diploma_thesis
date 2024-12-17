# Contextly
Contextly решает задачу скачавания видеo с Youtube сохранения его на сервере и извлечения аудио, текста и краткого содержание видео.

## Содержание
- [Технологии](#технологии)
- [Начало работы](#начало-работы)
- [Тестирование](#тестирование)
- [Deploy и CI/CD](#deploy-и-ci/cd)
- [Contributing](#contributing)
- [To do](#to-do)
- [Команда проекта](#команда-проекта)

## Технологии
- [Docker](https://www.docker.com/)
- [Python](https://www.python.org/)
- [FasAPI](https://fastapi.tiangolo.com/)
- [Tortoise ORM](https://tortoise.github.io/)
- [Torch](https://pytorch.org/)
- [Openai-Whisper](openai-whisper)
- ...

## Использование

Структура проекта:
```
Diploma_thesis/
├── contextly/
│   ├── __init__.py
│   ├── main.py                # Основной файл FastAPI с маршрутизацией
│   ├── routers/                   # API обработчики
│   │   ├── __init__.py
│   │   ├── static.py          # Обработчик для статики
│   │   ├── user.py            # Обработчик для работы с пользователями
│   │   └── video.py           # Обработчик для видео
│   ├── models/                # Модели для ORM Tortoise
│   │   ├── __init__.py
│   │   ├── user.py            # Модель для пользователя
│   │   └── video.py           # Модель для видео
│   ├── db.py                  # Конфигурация и подключение к базе данных
│   ├── utils/                 # Утилиты для работы с проектом
│   │   ├── __init__.py
│   │   ├── auth.py            # Утилиты для работы с JWT
│   │   └── youtubedl.py       # Утилиты для работы с базой данных
│   └── templates/             # Шаблоны Jinja2
│       └── index.html         # Пример шаблона
├── pyproject.toml           # Зависимости проекта
└── README.md                  # Документация проекта
```
Запуск из папки 
```sh
$ make install
$ make run
```
Запуск из докер контейнера
```sh
$ make docker
$ make docker_run
```