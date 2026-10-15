# Proxy image inherited from the previous team.

FROM nginx:alpine

COPY nginx.conf /etc/nginx/nginx.conf

RUN chown -R nginx:nginx /var/cache/nginx /run

EXPOSE 80

USER nginx
