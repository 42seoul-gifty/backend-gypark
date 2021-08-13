FROM python:3.9.2

ADD django_app/requirements.txt /
ADD .secrets /.secrets
RUN pip install --upgrade pip && \
    pip install -r requirements.txt
