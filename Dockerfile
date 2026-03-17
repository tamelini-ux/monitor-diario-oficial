FROM python:3.11

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "app.py"]
