FROM ghcr.io/weserv/images:sha-2b51dd8

ADD nginx.conf /etc/nginx/nginx.conf

CMD ["sh", "-c", "echo \"resolver $(awk '/nameserver/ {print $2}' /etc/resolv.conf);\" > /etc/nginx/conf.d/resolver.conf && exec nginx -g 'daemon off;'"]