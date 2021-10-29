#!/bin/bash

set -eu


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

ROOT_DIR=${SCRIPT_DIR}/..

BUILD_DIR=${ROOT_DIR}/tmp/local


cd ${ROOT_DIR}


mkdir -p ${BUILD_DIR}


jekyll clean -d ${BUILD_DIR} && jekyll serve -d ${BUILD_DIR}
