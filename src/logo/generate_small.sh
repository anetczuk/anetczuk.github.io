#!/bin/bash

set -eu

## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


SITE_DIR=$(realpath $SCRIPT_DIR/../../docs)


input_path=$SCRIPT_DIR/logo.png


## $1 -- size
## $2 -- output
resize_img() {
    local img_dim="$1"
    local img_output="$2"
    
    echo "converting: $input_path -> $img_output"
    convert $input_path -resize $img_dim $img_output
    #convert $input_path -resize 200x100 $small_name
}


resize_img 192 $SITE_DIR/android-chrome-192x192.png

resize_img 180 $SITE_DIR/apple-touch-icon.png

resize_img 32 $SITE_DIR/favicon-32x32.png

resize_img 96 $SITE_DIR/favicon-96x96.png

resize_img 310 $SITE_DIR/mstile-310x310.png
