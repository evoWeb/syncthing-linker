MAKEFLAGS += --warn-undefined-variables
SHELL := /bin/bash
.EXPORT_ALL_VARIABLES:
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.SILENT:


.PHONY: development
development:
	docker compose up -d syncthing
	docker compose up linker-development --remove-orphans
	docker compose down syncthing


.PHONY: connect
connect:
	docker compose exec linker-development sh


.PHONY: missing_files
missing_files:
	docker compose exec linker-development python missing_files.py


.PHONY: build
build:
	TAG=latest docker compose build linker-development
	docker image tag evoweb/syncthing-linker:latest evoweb/syncthing-linker:v1.0.0
.DEFAULT_GOAL := build
