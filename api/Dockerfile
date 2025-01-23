FROM python:3.11-alpine

WORKDIR /home/pgQueue

COPY ./pgqueue.py /home/pgQueue/
COPY ./requirements.txt /home/pgQueue/

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

CMD [ "fastapi", "run", "pgqueue.py", "--port", "8000" ]
