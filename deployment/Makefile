sync-certs:
	@./sync-certs.sh

release:
	@./release.sh

deploy-cpu: release
	@./deploy.sh authenticity-aws

deploy-gpu: release
	@./deploy.sh authenticity-aws-gpu

deploy-gpu2: release
	@./deploy.sh authenticity-aws-gpu2

deploy-ipc: release
	@./deploy.sh ipc

.PHONY: all $(MAKECMDGOALS)
