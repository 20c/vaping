FROM ubuntu:16.04

EXPOSE 7021

RUN apt-get update
RUN apt-get install -y python2.7 python2.7-dev python-pip
RUN pip install vaping
# requirements for examples/standalone_dns/
RUN pip install vodka graphsrv
RUN apt-get install -y fping

RUN mkdir /opt/vaping
WORKDIR /opt/vaping
# ENV VAPING_HOME /opt/vaping
ADD ./examples /opt/vaping/examples

# The process just silently exits without --debug in docker.
CMD vaping --home=/opt/vaping/examples/standalone_dns/ --verbose --debug start
