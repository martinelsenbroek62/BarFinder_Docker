FROM python:3.7-stretch AS builder
ENV LANG C.UTF-8
WORKDIR /app
COPY api_collection /app/api_collection/
COPY ["compile.py", "compile_all", "/_compile/"]
RUN pip install cython
RUN bash /_compile/compile_all

FROM python:3.7-stretch
ENV LANG C.UTF-8
WORKDIR /app
RUN apt-get update -qq && apt-get install -qqy libav-tools librtmp-dev
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt
ENV FFMPEG_CMD=avconv FLASK_APP=/app/api_collection/__init__.py
COPY --from=builder /app/build/lib.linux-x86_64-3.7/api_collection /app/api_collection/
# COPY api_collection /app/api_collection/
COPY entrypoint.sh run_socketio.py /app/
RUN chmod +x entrypoint.sh
EXPOSE 5000/tcp
EXPOSE 5001/tcp
EXPOSE 5555/tcp
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["app"]
