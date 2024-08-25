FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /bestview

COPY requirements.txt .

RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "bestviewproj.wsgi:application", "--bind", "0.0.0.0:8000"]