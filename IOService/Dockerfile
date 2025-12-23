# filepath: d:\FACULTATE George\Anul 4\Semestrul 2\IDP\idp_music\IOService\Dockerfile
FROM python:3.10

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=io_service.py

EXPOSE 5001

CMD ["python", "io_service.py"]