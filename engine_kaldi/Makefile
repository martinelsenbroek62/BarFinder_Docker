build-base:
	@docker build kaldi_base -t kaldi_base:latest

debug-base:
	@docker run --runtime nvidia -it --rm -v $(PWD)/shared:/shared kaldi_base:latest bash

build-datatang: build-base
	@cd datatang_mandarin; make build

build-diarization: build-base
	@docker build kaldi_diarization -t engine_diarization:latest

sync-tedlium:
	@bash -c 'source ../deployment/env.sh; aws s3 sync s3://xcellence-models/tedlium tedlium'

build-tedlium: build-base sync-tedlium
	@docker build tedlium -t engine_xcel2:latest-tedlium
	@docker build tedlium -t engine_xcel2:latest-tedlium-en-us --build-arg TEDLIUM_TARBALL=tedlium_en-US.tar.gz --build-arg TEDLIUM_DIR=/kaldi/egs/tedlium_19-08-23-17-31-10
	@docker build tedlium -t engine_xcel2:latest-tedlium-en-uk --build-arg TEDLIUM_TARBALL=tedlium_en-UK.tar.gz --build-arg TEDLIUM_DIR=/kaldi/egs/tedlium_19-08-22-21-05-49

debug-diarization:
	@docker run -it --rm -v $(PWD)/shared:/shared engine_diarization:latest bash

build: build-base build-diarization build-datatang build-tedlium
	@docker build . -t engine_xcel2:latest

debug:
	@docker run --runtime nvidia -it --rm -v $(PWD)/shared:/shared engine_xcel2:latest bash

debug-tedlium:
	@docker run --runtime nvidia -it --rm -v $(PWD)/shared:/shared engine_xcel2:latest-tedlium bash
