FROM python:3.10-slim

WORKDIR /var/www

COPY ./requirements.txt ./

# Install packages for the container
RUN apt-get update
RUN apt-get install -y pkg-config
RUN apt-get install -y python3-dev default-libmysqlclient-dev build-essential
RUN apt-get install -y firefox-esr

# Install python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["tail", "-f", "/dev/null"]
