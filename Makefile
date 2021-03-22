build-dial:
	@cd engine_dial && make build

build-kaldi:
	@cd engine_kaldi && make build

build-julius:
	@cd engine_julius && make build

build-frontend:
	@cd dial_frontend; make build

build: build-frontend
	@pipenv lock -r > requirements.txt
	@docker build . -t api_collection:latest
	# @PWD=$(shell pwd) docker-compose build

up: build
	@PWD=$(shell pwd) docker-compose up -d --remove-orphans

devdb:
	$(eval volumes = $(shell docker inspect -f '{{ range .Mounts }}{{ .Name }}{{ end }}' xcel-devdb))
	@docker rm -f xcel-devdb 2>/dev/null || true
	@docker volume rm $(volumes) 2>/dev/null || true
	@docker run \
		-d --name=xcel-devdb \
		--publish 127.0.0.1:5436:5432 \
		postgres:11

psql-devdb:
	@docker exec -it xcel-devdb psql -hlocalhost -U postgres

psql:
	@docker exec -it dialdocker_pgdb_1 psql -hlocalhost -U postgres

logs:
	@docker logs -f dialdocker_api_1

run: up logs

test:
	@python setup.py pytest

create-user:
	@docker exec -it dialdocker_api_1 flask users create

change-password:
	@docker exec -it dialdocker_api_1 flask users change-password

.PHONY: $(MAKECMDGOALS)
