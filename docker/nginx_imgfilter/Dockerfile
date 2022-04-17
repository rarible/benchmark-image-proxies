FROM debian:11

RUN apt update; apt -y install nginx

COPY nginx.conf /etc/nginx/nginx.conf

CMD nginx -g 'daemon off;'