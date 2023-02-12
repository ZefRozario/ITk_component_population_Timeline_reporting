# base image
FROM python:3.10

# Update package manager and get git
USER root
RUN apt-get update
RUN apt-get install -y git


RUN apt-get update && apt-get -y install cron vim
# make and set working directory
RUN mkdir /ext
RUN mkdir /code
COPY crontab /etc/cron.d/crontab
WORKDIR /code
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY cern_functions.py /ext
COPY write_only_loop.py /ext
# make directories
RUN mkdir ./streamlit
RUN mkdir ./streamlit/pages
RUN mkdir ./streamlit/htmls
RUN mkdir ./streamlit/scripts
RUN mkdir ./streamlit/outputs
# copy files
COPY streamlit/* ./streamlit/
#COPY streamlit/pages/* ./streamlit/pages/
#COPY streamlit/htmls/* ./streamlit/htmls/
#COPY streamlit/scripts/* ./streamlit/scripts/


# add user other than root (for cern deployment)
RUN adduser appuser
# tmp access for running app
RUN chown -R appuser:appuser /code/streamlit
RUN chmod 777 /code/streamlit
#RUN chmod 777 /code/streamlit/htmls
#RUN chmod 777 /code/streamlit/outputs
# tmp access for running app
RUN chown -R appuser:appuser /tmp
RUN chmod 777 /tmp
RUN chmod 777 /etc/cron.d/crontab
RUN /usr/bin/crontab /etc/cron.d/crontab


# exposing default port for streamlit
EXPOSE 8501 

# switch to appuser (for Cern)
USER appuser

WORKDIR /code/streamlit

CMD ["streamlit", "run", "app.py", "--server.port=8501"]
CMD ["cron", "-f"]
