FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN apt-get update

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python3", "./telegram-bot/doctordata_bot.py" ]
