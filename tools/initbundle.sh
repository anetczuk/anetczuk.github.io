#!/bin/bash

set -eu


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"


ROOT_DIR=${SCRIPT_DIR}/..

SITE_DIR=${ROOT_DIR}/docs

BUILD_DIR=${ROOT_DIR}/tmp/local


mkdir -p ${BUILD_DIR}

cd ${BUILD_DIR}


cp $SITE_DIR/Gemfile .
#### creates simple Gemfile
## bundle init

#### creates '.bundle/config' and 'vendor' dir
bundle install --path vendor/bundle

#### installs binaries to 'vendor' subdir
bundle add jekyll


#### following steps are not necessary

#### create content from minimal theme from template: '_posts', '_config.yml', '404.html', 'about.markdown', 'index.markdown'
## bundle exec jekyll new --force --skip-bundle .

#### installs additional binaries to 'vendor' subdir
## bundle install

#### build static site and run server
## bundle exec jekyll serve
