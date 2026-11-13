FROM ubuntu:24.04
LABEL org.opencontainers.image.source="https://github.com/rubiana-coin/rubiana"
RUN apt-get update && apt-get install -y --no-install-recommends libevent-2.1-7t64 libevent-pthreads-2.1-7t64 libsqlite3-0 ca-certificates && rm -rf /var/lib/apt/lists/*
COPY rubianad rubiana-cli /usr/local/bin/
COPY rubiana-start /usr/local/bin/rubiana-start
RUN chmod +x /usr/local/bin/rubianad /usr/local/bin/rubiana-cli /usr/local/bin/rubiana-start
EXPOSE 8686
CMD ["rubiana-start"]
