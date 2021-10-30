#!/bin/bash

set -eu


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"


ROOT_DIR=${SCRIPT_DIR}/..

SITE_DIR=${ROOT_DIR}/docs

BUILD_DIR=${ROOT_DIR}/tmp/local


cd ${BUILD_DIR}

bundle exec jekyll serve -s ${SITE_DIR}


## cd ${SITE_DIR}

## mkdir -p ${BUILD_DIR}

## jekyll clean -d ${BUILD_DIR} && jekyll serve -d ${BUILD_DIR}
