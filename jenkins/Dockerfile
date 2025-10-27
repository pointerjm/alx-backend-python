FROM jenkins/jenkins:lts-jdk17

USER root

# Install Python and build dependencies for mysqlclient
RUN apt-get update && \
    apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        pkg-config \
        default-libmysqlclient-dev \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

USER jenkins
