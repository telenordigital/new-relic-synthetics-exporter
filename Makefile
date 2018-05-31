BUILD_FOLDER=build
TMP_FILE=./$(BUILD_FOLDER)/build.zip

TMP_DELIVERABLE=$(abspath $(TMP_FILE))

install:
	pipenv install --three

uninstall:
	pipenv --rm

clean:
	rm -rf "${BUILD_FOLDER}"

build: Makefile new_relic_synthetics_exporter/*.py
	mkdir -p "${BUILD_FOLDER}"
	$(eval VENV = $(shell pipenv --venv))
	cd ${VENV}/lib/python3.6/site-packages && zip -r9 "${TMP_DELIVERABLE}" ./*
	cd new_relic_synthetics_exporter && zip -r9 "${TMP_DELIVERABLE}" *.py
	mv "$(TMP_DELIVERABLE)" "${BUILD_FOLDER}/new_relic_synthetics_exporter.zip"
