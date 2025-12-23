FROM python:3.10

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=auth.py

EXPOSE 5002

CMD ["python", "business.py"]
