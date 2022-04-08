ARG build_packages="\
    gcc \
    g++ \
    make \
    file \
    libc-dev \
    libffi-dev \
    curl \
    openssl-dev \
    make \
    rust \
    cargo \
    rrdtool-dev \
    "

ARG runtime_packages="fping librrd \
    zeromq \
    "
# vaping extras to be installed
ARG vaping_extras=all

ARG poetry_pin=">=1,<=2"

FROM python:3.9-alpine as base

ARG runtime_packages
ARG virtual_env=/venv

ENV VIRTUAL_ENV="$virtual_env"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"


# image that builds vaping and deps
FROM base as builder

ARG build_packages
ARG runtime_packages
ARG vaping_extras

RUN apk upgrade --available && apk --update --no-cache add $build_packages $runtime_packages

# install poetry outside of the venv
RUN pip install --upgrade pip wheel
# alpine package is currently only in edge
RUN pip install "poetry$poetry_pin"

# Create a VENV
RUN python3 -m venv "$VIRTUAL_ENV"

WORKDIR /src/vaping

COPY Ctl/VERSION Ctl/
COPY pyproject.toml poetry.lock README.md ./
COPY src src

# Need to upgrade pip and wheel within Poetry for all its installs
RUN poetry run pip install --upgrade pip wheel
# poetry installs a pth for root
RUN poetry install --no-dev --no-root
RUN poetry build -f wheel
RUN pip install "$(ls dist/vaping-*.whl)[all]"

# TODO testing stage in container for package deps, etc


# prep final running image
FROM base as final

ARG runtime_packages
ARG vaping_uid=1000

RUN apk upgrade --available \
    && apk --update --no-cache add $runtime_packages \
    && rm -rf /var/cache/apk/*

COPY --from=builder "$VIRTUAL_ENV" "$VIRTUAL_ENV"

RUN adduser -Du $vaping_uid vaping


# test against final image
FROM final as tester

ARG build_packages
ARG vaping_extras

WORKDIR /src/vaping

COPY pyproject.toml poetry.lock README.md ./
COPY src src
COPY tests tests

RUN env
# install dev
RUN apk --update add $build_packages
RUN pip install "poetry$poetry_pin"
RUN poetry install --no-root


# execute from final image
FROM final

ARG vaping_home=/vaping

ENV VAPING_HOME=$vaping_home

WORKDIR /vaping
RUN chown vaping:vaping /vaping

USER vaping
COPY --chown=vaping:vaping examples examples
COPY --chown=vaping:vaping examples/standalone_dns/config.yml .

EXPOSE 7021

# The process just silently exits without --debug in docker.
CMD ["vaping", "start", "--no-fork"]
