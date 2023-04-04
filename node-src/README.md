# Node service (Middleware)

## Introduction

This service is a middleware for connect telegram context backend and OpenAI's chatGPT model.

## Interface

| Interface name  | Description                                                                     | Params                      |
|-----------------|---------------------------------------------------------------------------------|-----------------------------|
| `/`             | Test interface. If service running normally, it will return "Hello world."      | None                        |
| `/emotion`      | Short encourage text interface, request GPT for a short text to encourage user. | mood(Optional): **str**     |
| `/review`       | Video comment generator, use GPT generates 2 comment for a movie.               | movie_name(Needed): **str** |
| `/recommend`    | Recommend some movie based on user's emotion situation                          | mood(Optional): **str**     |

## Configuration
Environment Requirement: see `requirements.txt`  
Nginx Config: Use `Nginx-upstream` to define the cluster, use `Nginx-proxy-pass` to redirect the requests.
```conf
# Define upstream servers for load balancing
upstream backend {
    server gpt-node01:4000;
    server gpt-node02:4000;
    server gpt-node03:4000;
    server gpt-node04:4000;
    server gpt-node05:4000;
}

# Redirect requests from port 80 to 4000
server {
    listen 80;
    #server_name _;
    location / {
        proxy_pass http://backend;
    }
}
```

## Project Structure
`docker-compose.yml` : Docker compose file to build up a cluster for five node services, with Nginx load-balance.  
`Dockerfile`: Simply build up a single node service, without nginx servie.(For docker-compose)  
`gpt.py`: A python class with GPT prompt processing.  
`log.py`: Build a log entity to log the information during service running.  
`nginx.conf`: Pre-set nginx config file, will load into nginx container during build up to compose.  
`nodeService.py`: The main service, using Flask to build up an API service to act as a middleware.  

## Install Env
To install env, use:
```bash
pip3 install -r requirements.txt
```

To build up a docker compose, use:
```bash
docker compose up -d docker-compose.yml
```

To build a single node service, use:
```bash
docker build -t node .

docker run -itd -p 80:80 --name nodetest node
```
