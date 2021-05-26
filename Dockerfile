FROM continuumio/miniconda3

# setup environment variable
ENV DockerHOME=/home/app/esapp

# set work directory
RUN mkdir -p $DockerHOME

# where your code lives
WORKDIR $DockerHOME

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy conda environment file:
COPY env.yaml $DockerHOME/env.yaml

# Update conda:
RUN conda update -n base -c defaults conda

# Create the environment:
RUN conda env create -f env.yaml

# copy whole project to your docker home directory.
COPY . $DockerHOME
