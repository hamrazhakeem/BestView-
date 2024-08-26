FROM python:3.10-slim

ENV PYTHONBUFFERED=1

WORKDIR /bestview

COPY requirements.txt requirements.txt
COPY . /bestview

RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt \
    && python manage.py collectstatic --noinput

CMD ["gunicorn", "bestviewproj.wsgi:application", "--bind", "0.0.0.0:8000"]