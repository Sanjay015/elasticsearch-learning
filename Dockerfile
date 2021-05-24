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

# Update conda:
RUN conda update -n base -c defaults conda

# Copy conda environment file:
COPY . $DockerHOME/env.yaml

# Create the environment:
RUN conda env create -f env.yaml

# copy whole project to your docker home directory.
COPY . $DockerHOME
