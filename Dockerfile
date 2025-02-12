FROM python:3.10

RUN apt-get update && apt-get install -y cron postgresql-client && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backup.py /app/backup.py
COPY .env /app/.env

RUN echo "0 0 * * * python3 /app/backup.py >> /var/log/cron.log 2>&1" > /etc/cron.d/backup-cron
RUN chmod 0644 /etc/cron.d/backup-cron && crontab /etc/cron.d/backup-cron

CMD ["cron", "-f"]