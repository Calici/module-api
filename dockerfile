FROM debian:12.2-slim

# Code here is executed as root

RUN useradd -u 8879 -m calici
RUN chown -R calici:calici /app

# Code here is executed as user

# Code after this is just preparation for running
WORKDIR /app
COPY ./src /app
ENTRYPOINT ["python3", "/app/run.py"]