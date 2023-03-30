FROM python:3.11.2
MAINTAINER cppfred<22443584@life.hkbu.edu.hk>
# mkdir
CMD mkdir /bot

# copy file to image
COPY ./ /bot/

# run pip install command when building image
RUN pip3 install pip update \
  && pip3 install --upgrade pip \
  && pip3 install -r /bot/requirements.txt

# set system enviroument
ENV BEARER_TOKEN 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

# set automatic command
CMD python3 /bot/nodeService.py
