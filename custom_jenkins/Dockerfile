
FROM jenkins/jenkins:lts

USER root

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        apt-transport-https ca-certificates curl gnupg lsb-release sudo && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends docker-ce docker-ce-cli containerd.io && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN groupadd -f docker && \
    usermod -aG docker jenkins && \
    echo "jenkins ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

RUN mkdir -p /var/lib/docker
VOLUME /var/lib/docker

USER jenkins
