build-gpu:
	@docker build -t local-deep-speech:latest-gpu --compress --build-arg BASEIMAGE=localpaddle:0.15.0-gpu-cuda9.2-cudnn7 .

build-cpu:
	@docker build -t local-deep-speech:latest-cpu --compress --build-arg BASEIMAGE=paddlepaddle/paddle:0.15.0 .

debug:
	@docker run -it --rm local-deep-speech:latest-cpu bash

debug-gpu:
	@docker run -it --rm local-deep-speech:latest-gpu bash
