build-paddle:
	@cd paddle-docker && make build

build-deep-speech: build-paddle
	@cd deep-speech-docker && make build-gpu build-cpu

build: build-deep-speech
	@docker build -t engine_dial:latest-gpu --build-arg BASEIMAGE=local-deep-speech:latest-gpu .
	@docker build -t engine_dial:latest-cpu --build-arg BASEIMAGE=local-deep-speech:latest-cpu .

debug:
	@docker run --runtime nvidia -it --rm -v $(PWD)/payload/models:/DecodeEngine/models -v $(PWD)/shared:/shared --entrypoint bash engine_dial:latest-gpu

debug-cpu:
	@docker run -it --rm -v $(PWD)/payload/models:/DecodeEngine/models -v $(PWD)/shared:/shared --entrypoint bash engine_dial:latest-cpu
