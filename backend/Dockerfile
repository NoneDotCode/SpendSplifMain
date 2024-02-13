FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir django gunicorn

COPY ../ /SpendSplif/backend

WORKDIR /SpendSplif

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
