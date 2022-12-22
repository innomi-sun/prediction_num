FROM python:3.8

WORKDIR /home/workdir

COPY requirements.txt /home/workdir
COPY uwsgi.ini /home/workdir
RUN pip install -r requirements.txt
# Run the command on container startup
# RUN cron && tail -f /home/prediction_num/log/LotteryDataJobFromContainer.log
# CMD uwsgi uwsgi.ini
CMD [ "sh", "-c", "uwsgi uwsgi.ini" ]