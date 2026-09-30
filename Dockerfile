FROM python:3.12-slim
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
RUN mkdir /data
ARG GIT_SHA=dev
ENV APP_VERSION=$GIT_SHA DB_PATH=/data/tasks.db
EXPOSE 8000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "app.app:create_app()"]
