FROM python:3.12-slim

ARG APP_VERSION=unknown
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_VERSION=${APP_VERSION}

WORKDIR /app

COPY app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

RUN mkdir -p logs media

RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "conf.wsgi:application", "-b", "0.0.0.0:8000"]
