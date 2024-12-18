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
├── Dockerfile                         # Докер файл для сборки проекта в контейнер
├── Makefile                           # Мейк содержит команды для удобной работы с проектом
├── README.md                          # Документация проекта
├── VERSION                            # Версия проекта
├── contextly/                         # Дирриктория исходного кода проекта
│   ├── __init__.py
│   ├── db.py                          # Конфигурация и подключение к базе данных
│   ├── favicon.ico                    # Изображение для отображения в заголовке браузера
│   ├── main.py                        # Основной файл FastAPI с маршрутизацией
│   ├── models/                        # Модели для ORM Tortoise
│   │   ├── __init__.py
│   │   ├── user.py                    # Модель для пользователя
│   │   └── video.py                   # Модель для видео
│   ├── routers/                       # API обработчики
│   │   ├── __init__.py
│   │   ├── static.py                  # Обработчик для статики
│   │   ├── user.py                    # Обработчик для работы с пользователями
│   │   └── video.py                   # Обработчик для видео
│   ├── settings.py                    # Настройки прокта
│   ├── templates/                     # Шаблоны Jinja2
│   │   ├── base.html                  # Базовый шаблон страницы
│   │   ├── download.html              # Шаблон страницы загрузки
│   │   ├── download_list.html         # Шаблон страницы всех загружкнных файлов
│   │   ├── index.html                 # Шаблон стартовой страницы
│   │   ├── login.html                 # Шаблон страницы ввода логина/пароля
│   │   ├── register.html              # Шаблон страницы регистрации 
│   │   └── video.html                 # Шаблон страницы загруженного видео
│   └── utils/                         # Утилиты для работы с проектом
│       ├── auth.py                    # Утилиты для авторизации сессии работы с JWT
│       ├── logger.py                  # Утилиты для логирования
│       ├── summarizer.py              # Утилиты содержит класс для сумаризации текста
│       ├── transcriber.py             # Утилиты содержит класс для преобразования голоса в текст
│       └── youtubedl.py               # Утилиты содержит класс для скачивания видео с Youtube
├── pyproject.toml                     # Зависимости проекта
├── tests/                             # Тесты
│   ├── conftest.py                    # Конфигурация тестов
│   └── pages_test.py                  # Тесты создания и авторизации пользователя
└── uv.lock                            # Файл фиксации зависимостей проекта
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