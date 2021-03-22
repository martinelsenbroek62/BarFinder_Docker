build:
	@docker build . -t localpaddle:0.15.0-gpu-cuda9.2-cudnn7

debug:
	@docker run --runtime nvidia -it --rm localpaddle:0.15.0-gpu-cuda9.2-cudnn7 bash
