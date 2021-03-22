#! /bin/bash

if [[ "$1" == "shell" ]]; then
    bash
    exit
fi

NGINX_SITE_CONF="/app/nginx.vh.xcellence.conf.template"

cp /app/nginx.conf /etc/nginx/nginx.conf
cp /app/xcellence_api_proxy.conf /etc/nginx/xcellence_api_proxy.conf

TLS_CONFIGURATION=""
if [ -d /etc/nginx/certs ]; then
    TLS_CONFIGURATION="\
    return 301 https://\$host\$request_uri;\n\
}\n\
\n\
server {\n\
    listen 443 default_server ssl;\n\
    server_name ${SERVER_NAME};\n\
    ssl_certificate /etc/nginx/certs/_.xcellence.tech.crt;\n\
    ssl_certificate_key /etc/nginx/certs/_.xcellence.tech.key;"
fi
cat $NGINX_SITE_CONF | sed -e "s#\!SERVER_NAME\!#${SERVER_NAME}#g; s#\!TLS_CONFIGURATION\!#${TLS_CONFIGURATION}#g" > /etc/nginx/sites-enabled/xcellence.conf
nginx -g "daemon off;"
