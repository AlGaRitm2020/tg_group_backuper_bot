Собрать образ:

```bash
docker build -t telegram-forward-bot .
```

Запустить бота:

```bash
docker run -d --env-file .env telegram-forward-bot
```

