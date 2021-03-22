build:
	@docker build . -t engine_julius:latest-ja

debug:
	@docker run -it --rm --runtime nvidia -v $(PWD)/shared:/shared -v $(PWD)/entrypoint.sh:/decode_engine/scripts/entrypoint.sh engine_julius:latest-ja bash
