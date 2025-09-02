FROM python:3.13-alpine3.21

ENV WMBC_VERSION=1.0.4
RUN adduser --disabled-password ct

RUN apk add --no-cache \
		build-base \
		bash \
		dpkg \
		elogind-dev \
		cairo-dev \
		gobject-introspection-dev \
		git

# TODO: install from PyPi after mainlining Wirepas changes
RUN git clone https://github.com/cthings-co/smpclient.git --branch wmbc && cd smpclient && pip3 install .
RUN git clone https://github.com/cthings-co/smpmgr.git --branch wmbc && cd smpmgr && pip3 install .
RUN wget https://raw.githubusercontent.com/cthings-co/wmb-controller/refs/tags/v${WMBC_VERSION}/scripts/fota.py
RUN chown ct:ct fota.py && mv fota.py /home/ct
USER ct
RUN pip3 install pygobject==3.50 wmbc==${WMBC_VERSION}

CMD ["python3", "-m", "wmbc", "--help"]
