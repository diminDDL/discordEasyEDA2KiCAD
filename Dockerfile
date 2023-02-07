# Based on https://github.com/ThatRedKite/thatkitebot/
# FROM python:3.10-bullseye
FROM ubuntu:latest

WORKDIR /app/

COPY ./requirements.txt /tmp/requirements.txt
COPY ./bot /app/bot

WORKDIR /tmp/

# Yes we really need to install kicad

RUN apt-get update && apt-get upgrade -y

RUN apt-get install -y python3 python3-pip git openctm-tools npm zip software-properties-common libgtk2.0-dev

RUN add-apt-repository --yes ppa:kicad/kicad-6.0-releases

RUN npm install -g easyeda2kicad

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

RUN apt-get update --allow-insecure-repositories

RUN apt-get install --install-recommends -y kicad

# until https://github.com/Pycord-Development/pycord/issues/1840 is fixed we have to use an older version
# RUN pip3 install -U "py-cord[speed]"
RUN pip3 install -U "py-cord[speed]"==2.3.0

WORKDIR /app/

RUN git clone https://github.com/yaqwsx/EasyEDAFootprintScraper

