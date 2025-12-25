FROM python:3-trixie

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app /usr/src/

CMD [ "python", "./main.py" ]