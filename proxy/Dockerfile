# Proxy image inherited from the previous team.

FROM ubuntu:24.04

COPY nginx.conf /etc/nginx/nginx.conf

RUN apt-get update && \
    apt-get install -y nginx curl htop vim git

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
