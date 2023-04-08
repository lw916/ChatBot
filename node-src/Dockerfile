FROM python:3.11.2
MAINTAINER cppfred<22443584@life.hkbu.edu.hk>

# SET DIRECTORY
WORKDIR /bot/node-src/

# copy file to image
COPY ./ /bot/node-src/

# run pip install command when building image
# when using apt install something need to mannully
RUN apt update -y \
  && apt install -y python3-pip \
  && pip install pip update \
  && pip install --upgrade pip \
  && pip install -r /bot/node-src/requirements.txt

# set system enviroument
ENV BEARER_TOKEN Please enter your chatgpt api key

# set automatic command
CMD python3 /bot/node-src/nodeService.py
