# pull official base image
FROM python:3

# set work directory
WORKDIR /app

# install dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy project
COPY . .
