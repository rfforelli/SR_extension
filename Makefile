help:
	@echo "INFO: make <tab> to list the tabs"
.PHONY: help

run:
	python parse_model.py
.PHONY: run

clean:
	rm -rf test_model
	rm -f test_model.tar.gz
.PHONY: clean
