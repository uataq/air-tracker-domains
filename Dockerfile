FROM python:3.9.0-buster

WORKDIR /src

ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONUNBUFFERED 1
ENV TZ UTC

# RUN apt-get update \
#     && apt-get install -y --no-install-recommends \
#     build-essential \
#     git \
#     libhdf5-serial-dev \
#     libmagic-dev \
#     libnetcdf-dev \
#     libssl-dev \
#     locales \
#     netcdf-bin \
#     procps \
#     r-base \
#     r-base-dev \
#     unzip \
#     wget \
#     && locale-gen en_US.UTF-8 \
#     && update-locale \
#     && rm -rf /var/lib/apt/lists/*

# Tini is an init replacement to reap child processes and sure proper signal handling.
# Kubernetes will (in most cases) send SIGTERM to PID 1 prior to evicting a pod. Tini
# will terminate PID 1 on SIGTERM so we don't need to configure a separate signal
# handler at runtime.
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]

# Install python dependencies.
COPY . .
RUN pip install --upgrade pip \
    && pip install .

CMD [ "python", "scene_generator.py" ]
