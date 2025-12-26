MAKEFLAGS += --warn-undefined-variables
SHELL := /bin/bash
.EXPORT_ALL_VARIABLES:
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.SILENT:


.PHONY: development
development:
	docker compose up linker-development


.PHONY: connect
connect:
	docker compose exec linker-development bash


.PHONY: build
build:
	TAG=v1.0.0 docker compose build linker-development
.DEFAULT_GOAL := build
