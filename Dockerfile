ARG dep_packages="fping"

FROM python:3.9-alpine as base

ARG virtual_env=/venv

ENV VIRTUAL_ENV="$virtual_env"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV POETRY_VERSION=1.1.4


# image that builds vaping and deps
FROM base as builder

RUN apk --update --no-cache add gcc g++ make file libc-dev libffi-dev curl openssl-dev make $dep_packages

# Install Rust to install Poetry
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Use Pip to install Poetry
RUN pip install "poetry==$POETRY_VERSION"

# Create a VENV
RUN python3 -m venv "$VIRTUAL_ENV"

WORKDIR /build

# individual files here instead of COPY . . for caching
COPY pyproject.toml poetry.lock ./

# Need to upgrade pip and wheel within Poetry for all its installs
RUN poetry run pip install --upgrade pip
RUN poetry run pip install --upgrade wheel
RUN poetry install --no-root

COPY Ctl/VERSION Ctl/

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