---

# Бэкап PostgreSQL в S3-совместимое хранилище с уведомлением в Telegram

Данный скрипт на Python создаёт бэкап базы данных PostgreSQL, загружает его в S3-совместимое хранилище (например, Cloudflare R2) и отправляет уведомление в Telegram о статусе выполнения (успешно или с ошибкой).

## Возможности
- Создание дампа PostgreSQL в файл.
- Загрузка дампа в S3-совместимое хранилище.
- Отправка уведомлений в Telegram о результатах выполнения.
- Использование переменных окружения для настройки.

## Требования
- Python 3.9+
- PostgreSQL-клиент (`pg_dump` должен быть установлен)
- Доступ к S3-совместимому хранилищу (например, AWS S3 или Cloudflare R2)
- Telegram-бот и chat ID для получения уведомлений.

## Установка

1. Склонируйте репозиторий:
```sh
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

2. Установите зависимости:
```sh
pip install -r requirements.txt
```

3. Убедитесь, что `pg_dump` установлен:
```sh
apt-get update && apt-get install -y postgresql-client
```

## Конфигурация

Создайте файл `.env` в корневой папке проекта со следующими переменными:

```env
# Конфигурация PostgreSQL
PG_HOST=your_pg_host
PG_USER=your_pg_user
PG_DATABASE=your_pg_database
PG_PASSWORD=your_pg_password
DUMP_FILE_NAME=dump.sql

# Конфигурация S3
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
CLOUDFLARE_R2_ENDPOINT=https://your-r2-endpoint
BUCKET_NAME=your_bucket_name
S3_PREFIX=backups

# Конфигурация Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

## Использование

1. Запустите скрипт вручную:
```sh
python backup.py
```

2. **(Опционально)** Настройте запуск каждый день в 00:00 через Docker и cron:
- Создайте Dockerfile, который устанавливает `cron` и запускает скрипт по расписанию.
- Пример Dockerfile и инструкции можно найти в этом репозитории (см. раздел Docker).

## Логи

- Логи выполнения скрипта сохраняются в стандартный вывод (`stdout`).
- Уведомления о статусе приходят в Telegram.

## Возможные ошибки
- `pg_dump: not found`: Убедитесь, что PostgreSQL-клиент установлен.
- Ошибка отправки в Telegram: Проверьте `TELEGRAM_BOT_TOKEN` и `TELEGRAM_CHAT_ID`.
- Ошибка загрузки в S3: Убедитесь, что доступ к вашему S3-совместимому хранилищу корректно настроен.

## Лицензия
Этот проект распространяется под лицензией MIT.
