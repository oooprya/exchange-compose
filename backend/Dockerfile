FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .
# RUN sed -i 's/\r$//g' /usr/src/app/entrypoint.sh
# RUN chmod +x /usr/src/app/entrypoint.sh

COPY . .

# run entrypoint.sh
# ENTRYPOINT ["/usr/src/app/entrypoint.sh"]