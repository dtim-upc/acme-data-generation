.DEFAULT_GOAL := help
.PHONY: help

#include .env
export

# taken from https://container-solutions.com/tagging-docker-images-the-right-way/

help: ## Print this help
	@grep -E '^[a-zA-Z_-\.]+:.*?## .*$$' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

shell: ## Activate venv using poetry
	poetry shell

test: ## Run tests with pytest
	poetry run pytest tests

coverage: ## Run tests with pytest and coverage
	poetry run pytest --cov=acme_data_generation tests

memprofile.generate: ## Run memory profile with FIL
	poetry run fil-profile run project/scripts/generate.py

business-rules: ## Convert markdown to pdf (just because I am lazy)
	poetry run pandoc -s docs/business_rules.md -o docs/business_rules.pdf --template eisvogel
