FROM python:3.6.0

RUN mkdir -p /app
WORKDIR /app
COPY . /app/

RUN pip install -r requirements/prod.txt
RUN python3 manage.py migrate

EXPOSE 8000

CMD uwsgi --http :8000 --module hbnn.wsgi

