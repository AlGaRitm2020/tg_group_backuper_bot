# Телеграм бот архиватор

## Запуск

Через docker-compose:

```bash
docker compose up --build -d
```

Собрать образ:

```bash
docker build -t telegram-forward-bot .
```

Запустить бота:

```bash
docker run -d --env-file .env telegram-forward-bot
```

## Как пользоваться Makefile

- make venv → создать виртуальное окружение
- make sync → скачать зависимости
- make dev → запустить бота локально
- make build → пересобрать docker image
- make up → поднять docker-compose
- make logs → показать логи бота
- make down → остановить контейнер
