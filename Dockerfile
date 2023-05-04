FROM python

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

RUN pip install --upgrade pip
COPY ./educa/requirements.txt /code/
COPY ./wait-for-it.sh /code/
RUN pip install -r requirements.txt
RUN mkdir -p /var/www/uwsgi
RUN mkdir -p /static/
RUN chown -R www-data:www-data /var/www/uwsgi
COPY ./educa/ /code/educa
