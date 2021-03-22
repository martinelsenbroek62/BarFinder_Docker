0002_cvte_chain_model_v2.tar.gz:
	@curl http://kaldi-asr.org/models/2/0002_cvte_chain_model_v2.tar.gz -o 0002_cvte_chain_model_v2.tar.gz

build: 0002_cvte_chain_model_v2.tar.gz
	@docker build . -t engine_xcel2:latest-mandarin

debug:
	@docker run --runtime nvidia -it --rm -v $(PWD)/../shared:/shared engine_xcel2:latest-mandarin bash

debug-cpu:
	@docker run -it --rm -v $(PWD)/../shared:/shared engine_xcel2:latest-mandarin bash
