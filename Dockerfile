FROM continuumio/miniconda3

# setup environment variable
ENV DockerHOME=/home/app/webapp

# set work directory
RUN mkdir -p $DockerHOME

# where your code lives
WORKDIR $DockerHOME

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# port where the Django app runs
EXPOSE 8000

# Copy conda environment file:
COPY env.yaml $DockerHOME/env.yaml

# Update conda:
RUN conda update -n base -c defaults conda

# Create the environment:
RUN conda env create -f env.yaml

# copy whole project to your docker home directory.
COPY . $DockerHOME

# make entrypoint script executable
RUN chmod u+x $DockerHOME/entrypoint.sh
RUN chmod u+x $DockerHOME/run.sh

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "transactionretrieval", "/bin/bash", "-c"]

# The code to run when container is started:
ENTRYPOINT ["/home/app/webapp/entrypoint.sh"]

CMD ["./run.sh"]
