FROM python:3.13-alpine3.21

RUN adduser --disabled-password ct

RUN apk add --no-cache \
		build-base \
		bash \
		dpkg \
		elogind-dev \
		cairo-dev \
		gobject-introspection-dev

USER ct
RUN pip3 install pygobject==3.50 wmbc==1.0.0

CMD ["python3", "-m", "wmbc", "--help"]
