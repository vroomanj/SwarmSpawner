FROM centos:latest
ENV container docker

MAINTAINER Justin Vrooman <vroomanj@egr.msu.edu>

# Set env vars related to language encoding
ENV LANGUAGE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV PYTHONIOENCODING UTF-8

# Disable core dumps
RUN ulimit -c 0

# Update/upgrade the base image
RUN yum -y update && \
    yum -y upgrade && \
    yum clean all

# Install the EPEL repo
RUN yum -y install epel-release && \
    yum clean all

# Install various packages
RUN yum -y install sssd-client \
                   wget \
                   git \
                   bzip2 && \
    yum clean all

# Download the latest tini (init for containers)
RUN curl -L https://github.com/krallin/tini/releases/download/v0.14.0/tini > tini && \
    echo 'eeffbe853a15982e85d923390d3a0c4c5bcf9c78635f4ddae207792fa4d7b5e6 *tini' | sha256sum -c - && \
    mv tini /usr/local/bin/tini && \
    chmod +x /usr/local/bin/tini

# Add jupyter group and user
RUN groupadd --gid 1000 jupyter && \
    useradd --uid 1000 --gid jupyter --home-dir /etc/jupyterhub --create-home jupyter

# Add the PAM module
ADD other-files/sss-proxy /etc/pam.d/system-auth

# Install Miniconda (python3)
RUN wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/miniconda3 && \
    rm -f Miniconda3-latest-Linux-x86_64.sh

# Add Miniconda3 to PATH and setup CONDA_PREFIX
ENV PATH /opt/miniconda3/bin:$PATH
ENV CONDA_PREFIX /opt/miniconda3

# Install SwarmSpawner
RUN cd /tmp && \
    git clone https://github.com/vroomanj/SwarmSpawner.git && \
    cd SwarmSpawner && \
    pip install -r requirements.txt && \
    python3 setup.py install && \
    cd ~ && \
    rm -rf /tmp/SwarmSpawner && \
    rm -rf /root/.cache

# Install JupyterHub and dependencies
RUN conda install -c conda-forge sqlalchemy tornado jinja2 traitlets requests pip nodejs configurable-http-proxy jupyterhub && \
    pip install --upgrade pip && \
    conda clean --index-cache --lock --tarballs --source-cache && \
    rm -rf /root/.cache

# Add some files and directories
VOLUME /etc/jupyterhub
#ADD other-files/jupyterhub_config.py /etc/jupyterhub
#RUN chown -R jupyter:jupyter /etc/jupyterhub && \
#    chmod 0640 /etc/jupyterhub/* && \

VOLUME /srv/jupyterhub
#RUN mkdir -p /srv/jupyterhub/ssl
#ADD other-files/srv/. /srv/jupyterhub
#RUN chown -R jupyter:jupyter /srv/jupyterhub && \
#    chmod 0640 /srv/jupyterhub/* && \
#    chown root:jupyter /srv/jupyterhub/ssl && \
#    chmod 0750 /srv/jupyterhub/ssl && \
#    chmod 0600 /srv/jupyterhub/ssl/*

#VOLUME /log/jupyterhub
RUN mkdir -p /log/jupyterhub && \
    chown -R jupyter:jupyter /log/jupyterhub && \
    chmod -R 0755 /log

# Set the working directory
WORKDIR /srv/jupyterhub/

# Expose JupyterHub port
EXPOSE 8000

# Add a label
LABEL org.jupyter.service="jupyterhub"

# Create an entry point and run JupyterHub as jupyter user
USER jupyter
ENTRYPOINT ["tini", "--"]
CMD ["jupyterhub", "-f", "/etc/jupyterhub/jupyterhub_config.py"]
