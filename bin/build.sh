#! /bin/bash
poetry install
poetry export -f requirements.txt --output src/requirements.txt # export the dependency list for sam
j2 sam/template.yaml --filters bin/j2_custom_filters.py > template.yaml
sam build
