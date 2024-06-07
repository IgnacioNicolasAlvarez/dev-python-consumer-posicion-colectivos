FROM python:3.12.3-alpine 

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN adduser -D containeruser

USER containeruser

WORKDIR /usr/src/app

CMD ["python", "./main.py"]