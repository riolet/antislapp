FROM python:2.7.13-wheezy

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

RUN chown -R :0 /app && chmod -R 775 /app && chmod g+s /app

WORKDIR /app/antislapp 

CMD python index.py
