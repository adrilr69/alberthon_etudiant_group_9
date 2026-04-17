FROM python:latest

WORKDIR /app

RUN pip install google-cloud-aiplatform requests streamlit pandas openpyxl

ADD . /app

ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/letudiant-data-prod-albert.json