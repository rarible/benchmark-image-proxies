FROM python:3.10-slim-bullseye

RUN pip install fastapi fastapi-utils aiohttp uvicorn pillow

ADD app*.py /

CMD uvicorn app:app --host 0.0.0.0 --port 8000 --workers 1 --no-access-log