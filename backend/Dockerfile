FROM python:3.11-slim
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .
RUN chmod +x /entrypoint.sh

COPY . .

# run entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]