FROM python:3.10

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=auth.py

EXPOSE 5000

CMD ["python", "auth.py"]
