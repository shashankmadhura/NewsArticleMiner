FROM python:3.9.6

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["python3", "pipeline.py"]
