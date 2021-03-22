FROM node:12 as builder
ENV LANG C.UTF-8
WORKDIR /app
COPY package*.json yarn.lock /app/
RUN yarn
COPY public /app/public
COPY src /app/src
RUN yarn build

FROM ubuntu:18.04
ENV LANG C.UTF-8
RUN apt-get update -qqy && \
    apt-get install -qy nginx-full && \
    rm /etc/nginx/sites-enabled/*
WORKDIR /app
COPY dockerfiles/* /app/
COPY --from=builder /app/build /app/html
EXPOSE 80/tcp
EXPOSE 443/tcp
ENTRYPOINT ["/app/entrypoint.sh"]
