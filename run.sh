#!/bin/bash
# this is a general setup script for this project


# train a tagger model with option --train, -t
PARAMS_TRAIN=0

# predict sem-tags for unlabeled data with option --predict, -p
PARAMS_PREDICT=0

# set bash to 'debug' mode, it will exit on :
# -e 'error', -u 'undefined variable', -o ... 'error in pipeline', -x 'print commands'
set -e
set -u
set -o pipefail
#set -x

# ensure script runs from the root directory
DIR_ROOT=${PWD}
if ! [ -x ${DIR_ROOT}/run.sh ]; then
    echo '[INFO] You must execture run.sh from the root directory'
    exit 1
fi

# load configuration options
. ${DIR_ROOT}/config.sh

# transform long options to short ones and parse them
for arg in "$@"; do
    shift
    case "$arg" in
        "--train") set -- "$@" "-t" ;;
        "--predict") set -- "$@" "-p" ;;
        *) set -- "$@" "$arg"
    esac
done

while getopts s:tp option
do
    case "${option}"
    in
        t) PARAMS_TRAIN=1;;
        p) PARAMS_PREDICT=1;;
    esac
done


if [ ${PARAMS_TRAIN} -ge 1 ]; then
	# DOWNLOAD AND PREPARE DATA
	echo '[INFO] Preparing data...'
	. ${DIR_DATA}/prepare_data.sh
	echo '[INFO] Finished preparing data'

	# SETUP REQUIRED TOOLS
	echo '[INFO] Setting up required tools...'
	. ${DIR_TOOLS}/prepare_tools.sh
	echo '[INFO] Finished setting up tools'

	# TRAIN A MODEL
	echo "[INFO] Training a ${MODEL_TYPE} model for semantic tagging..."
	. ${DIR_MODELS}/semtagger_train.sh
	echo '[INFO] A model was succesfully trained'
fi


if [ ${PARAMS_PREDICT} -ge 1 ]; then
	# PREDICT USING A TRAINED MODEL
	echo "[INFO] Predicting sem-tags using a ${MODEL_TYPE} model..."
	. ${DIR_MODELS}/semtagger_predict.sh
	echo '[INFO] Finished tagging'
fi

