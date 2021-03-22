ARG dep_packages="fping"

FROM python:3.7-alpine as base

ARG virtual_env=/venv

ENV VIRTUAL_ENV="$virtual_env"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"


# image that builds vaping and deps
FROM base as builder

RUN apk --update --no-cache add gcc g++ make file libc-dev libffi-dev py-gevent $dep_packages

# create venv
RUN python3 -m venv "$VIRTUAL_ENV"
RUN pip install -U pip pipenv

# requirements for examples/standalone_dns/
RUN pip install \
	graphsrv \
	vodka

WORKDIR /src/vaping
ADD . .

RUN pip install .


# final running image
FROM base

ARG dep_packages
ARG vaping_home=/app/examples/standalone_dns/
ARG vaping_uid=1000

ENV VAPING_HOME=$vaping_home
#ENV VAPING_UID=$vaping_uid

RUN apk --update --no-cache add $dep_packages

COPY --from=builder "$VIRTUAL_ENV" "$VIRTUAL_ENV"

RUN adduser -Du $vaping_uid vaping

WORKDIR /app
COPY --chown=$vaping_uid:$vaping_uid --from=builder /src/vaping/examples examples/

USER vaping
EXPOSE 7021

# The process just silently exits without --debug in docker.
CMD ["vaping", "--verbose", "--debug", "start"]