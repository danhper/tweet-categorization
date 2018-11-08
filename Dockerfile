FROM python:3.6.1

WORKDIR /usr/src/app
COPY . /usr/src/app

RUN pip install --no-cache-dir -r requirements.txt

#CMD [ "/bin/bash", "-c", "python importer.py" ]