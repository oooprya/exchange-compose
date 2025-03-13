FROM python:3.9-slim

# set work directory
WORKDIR /usr/src/app/


# Install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt


# Copy project
COPY . .

# run app
CMD ["python", "main.py"]