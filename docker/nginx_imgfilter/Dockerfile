FROM debian:11

RUN apt update; apt -y install nginx

COPY nginx.conf /etc/nginx/nginx.conf

CMD ["sh", "-c", "echo \"resolver $(awk '/nameserver/ {print $2}' /etc/resolv.conf);\" > /etc/nginx/conf.d/resolver.conf && exec nginx -g 'daemon off;'"]