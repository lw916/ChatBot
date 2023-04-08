FROM python
WORKDIR /bot
COPY ./ /bot/
RUN pip install --upgrade pip \
&& pip install -r requirements.txt
ENV ACCESS_TOKEN Please enter your telegram database api key
ENV HOST chatbot.redis.cache.windows.net
ENV PASSWORD Please enter your databse password
ENV PORT 6379

ENTRYPOINT ["python", "/bot/bin/start.py"]