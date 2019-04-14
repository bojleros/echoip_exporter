FROM alpine:3.9

RUN apk --no-cache add python3 py3-requests && \
    pip3 install prometheus-client && \
    rm -rf /var/cache/apk/*

ENV APP_DIR /app

COPY app/* /app/

WORKDIR /app

ENTRYPOINT ["python3"]

CMD ["-u", "main.py"]
