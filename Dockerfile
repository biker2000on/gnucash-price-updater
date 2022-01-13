FROM python:3-bullseye

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apt-get update \
  ^^ apt-get install -y cron \
  && pip install --no-cache-dir -r requirements.txt

COPY . .
COPY crontab /etc/cron.d/crontab

RUN chmod 0644 /etc/cron.d/crontab && \
    crontab /etc/cron.d/crontab

# CMD [ "python", "./gnucash-updater.py" ]
ENTRYPOINT [ "cron", "-f" ]
