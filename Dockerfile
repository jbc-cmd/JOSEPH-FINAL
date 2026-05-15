FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY flowershop/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

COPY flowershop/ /app/
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py init_data && python manage.py create_admin_account --username \"$ADMIN_USERNAME\" --email \"$ADMIN_EMAIL\" --password \"$ADMIN_PASSWORD\" && gunicorn flowershop_project.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]
