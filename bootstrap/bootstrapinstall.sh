#!/usr/bin/env bash
# shellcheck disable=SC2034
PYTHON="python"
ENTRYPOINT="bootstrap_install.py"

pushd ${0%/*} > /dev/null || (echo "ERROR: Could not pushd to current directory" && exit 1)
WORKING_DIR=$(pwd)
VIRTUALENV="${WORKING_DIR}/virtualenv"
ACTIVATE="${VIRTUALENV}/bin/activate"
REQ="${WORKING_DIR}/src/conf/requirements.txt"
COMMAND="${WORKING_DIR}/src/${ENTRYPOINT}"
popd > /dev/null || (echo "ERROR: Could not popd" && exit 1)
# shellcheck source=.bootstrap.sh
source "${WORKING_DIR}/.bootstrap.sh"
${PYTHON} "${COMMAND}" $@
