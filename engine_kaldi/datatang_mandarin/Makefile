0010_aidatatang_asr.tar.gz:
	@curl http://kaldi-asr.org/models/10/0010_aidatatang_asr.tar.gz -o 0010_aidatatang_asr.tar.gz

build: 0010_aidatatang_asr.tar.gz
	@docker build . -t engine_xcel2:latest-mandarin

debug:
	@docker run --runtime nvidia -it --rm -v $(PWD)/../shared:/shared engine_xcel2:latest-mandarin bash

debug-cpu:
	@docker run -it --rm -v $(PWD)/../shared:/shared engine_xcel2:latest-mandarin bash
