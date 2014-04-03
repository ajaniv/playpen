#!/usr/bin/env bash

#
# Dump application data from db to json file
# 
# 
set -e
set -x 
MY_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source ${MY_DIR}/common.sh
MY_ARGS="${DUMPDATA_ARGS}  $SETTINGS_ARGS  $VERBOSITY_ARGS"
MY_CMD="python $MANAGE_CMD dumpdata"
. ${VENV_LOCAL_DIR}/bin/activate

for i in "${APP_FIXTURE_LIST[@]}"
do
    echo "dumping $i"
    cd $ROOT_DIR && $MY_CMD $i  $MY_ARGS > ${FIXTURE_DIR}/${i}.json  
done

echo "dumping ${AUTH_FIXTURE_LIST[@]}"
cd $ROOT_DIR && $MY_CMD ${AUTH_FIXTURE_LIST[@]} $MY_ARGS > ${FIXTURE_DIR}/auth.json

