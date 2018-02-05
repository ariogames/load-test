#set django base image
FROM docker.ariogames.ir/python:3.6

RUN apt-get update
RUN apt-get install -y python3-dev libpq-dev

# Install required packages and remove the apt packages cache when done.
RUN apt-get install -y --no-install-recommends
RUN rm -rf /var/lib/apt/lists/*

# COPY requirements.txt and RUN pip install BEFORE adding the rest of your code, this will cause Docker's caching mechanism
# to prevent re-installing (all your) dependencies when you made a change a line or two in your app.
COPY requirements.txt ./
RUN pip install -r requirements.txt

# copy rest of project
COPY . .

EXPOSE 8089
EXPOSE 5557
EXPOSE 5558

CMD locust --slave --master-host=$LOCUST_MASTER_IP_ADDR