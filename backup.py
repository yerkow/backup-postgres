import os
import boto3
from botocore.exceptions import NoCredentialsError
from datetime import datetime
from dotenv import load_dotenv
import requests
import schedule
import time

# Load environment variables from .env file
load_dotenv()


def send_telegram_message(message):
    """Send a message to Telegram chat."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID не заданы.", flush=True)
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}

    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("Уведомление успешно отправлено в Telegram.", flush=True)
        else:
            print(
                f"Ошибка при отправке уведомления: {response.status_code}, {response.text}",
                flush=True,
            )
    except Exception as e:
        print(f"Ошибка при отправке уведомления: {e}", flush=True)


def upload_to_s3(source_path, destination_filename, bucket_name):
    """Upload file to S3-compatible storage."""
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            endpoint_url=os.getenv("CLOUDFLARE_R2_ENDPOINT"),
        )

        s3.upload_file(source_path, bucket_name, destination_filename)
        print(
            f"Файл успешно загружен в {bucket_name}/{destination_filename}", flush=True
        )

    except NoCredentialsError:
        raise Exception("Ошибка: нет учетных данных для AWS.")
    except Exception as e:
        raise Exception(f"Ошибка при загрузке файла в S3: {e}")


def main():
    try:
        # Get PostgreSQL parameters from environment variables
        pg_host = os.getenv("PG_HOST")
        pg_user = os.getenv("PG_USER")
        pg_database = os.getenv("PG_DATABASE")
        pg_password = os.getenv("PG_PASSWORD")
        dump_file = os.getenv("DUMP_FILE_NAME")
        prefix = os.getenv("S3_PREFIX")
        bucket_name = os.getenv("BUCKET_NAME")

        # Проверка обязательных переменных
        required_vars = {
            "PG_HOST": pg_host,
            "PG_USER": pg_user,
            "PG_DATABASE": pg_database,
            "PG_PASSWORD": pg_password,
            "DUMP_FILE_NAME": dump_file,
            "S3_PREFIX": prefix,
            "BUCKET_NAME": bucket_name,
        }

        for var, value in required_vars.items():
            if not value:
                raise ValueError(f"Переменная окружения {var} не найдена в .env")

        # Установить переменную окружения для пароля PostgreSQL
        os.environ["PGPASSWORD"] = pg_password

        # Создать дамп базы данных
        dump_command = f"pg_dump -h {pg_host} -U {pg_user} {pg_database} > {dump_file}"
        os.system(dump_command)

        # Проверить, создан ли дамп и его размер
        if os.path.exists(dump_file) and os.path.getsize(dump_file) > 0:
            timestamp = datetime.strftime(datetime.now(), "%Y.%m.%d.%H:%M")
            destination_filename = (
                f"{prefix}/{os.path.splitext(dump_file)[0]}_{timestamp}UTC.sql"
            )
            upload_to_s3(dump_file, destination_filename, bucket_name)
            send_telegram_message(
                f"✅ Бэкап {destination_filename} успешно загружен в R2."
            )
        else:
            send_telegram_message(
                f"❌ Ошибка: файл дампа {dump_file} пустой или не создан."
            )

    except Exception as e:
        send_telegram_message(f"❌ Ошибка при выполнении бэкапа: {e}")


def job():
    """Функция, оборачивающая запуск основного процесса бэкапа."""
    print("Запуск процесса бэкапа...", flush=True)
    main()
    print("Процесс бэкапа завершён.", flush=True)


if __name__ == "__main__":
    # Настройка расписания: запускать бэкап каждый день в 00:00
    schedule.every().day.at("00:00").do(job)
    print("Планировщик запущен. Ожидание выполнения задач...", flush=True)

    # Запуск цикла планировщика
    while True:
        schedule.run_pending()
        time.sleep(60)  # Проверять расписание каждую минуту
