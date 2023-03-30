FROM python
RUN mkdir /bot
WORKDIR /bot
COPY ./ /bot/
RUN pip install --upgrade pip \
&& pip install -r requirements.txt
ENV ACCESS_TOKEN 6074549142:AAF2SzhninDmgBLrrYrjXYrdHubvk73ATpM
ENV HOST chatbot.redis.cache.windows.net
ENV PASSWORD Esnm5uGsCpdfFvVWRaKzhAQ8Dt8T8wMPQAzCaFHSGms=
ENV PORT 6379

ENTRYPOINT ["python", "/bot/bin/start.py"]