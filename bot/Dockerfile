FROM python:3.9-alpine

# set work directory
WORKDIR /usr/src/app/

ENV TZ=Europe/Kyiv
RUN apk add tzdata && \
    cp /usr/share/zoneinfo/Europe/Kyiv /etc/localtime && \
    echo "Europe/Kyiv" > /etc/timezone

# Install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt


# Copy project
COPY . .


# # run app
CMD ["python", "main.py"]