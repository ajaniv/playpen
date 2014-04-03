#!/usr/bin/env bash
#
# Upload  json data files into database
#
set -e

MY_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source ${MY_DIR}/common.sh
MY_ARGS="$SETTINGS_ARGS  $VERBOSITY_ARGS"
MY_CMD="python $MANAGE_CMD loaddata"
. ${VENV_LOCAL_DIR}/bin/activate

for i in "${FIXTURE_LIST[@]}"
do
    echo "loading $i"
	cd $ROOT_DIR && $MY_CMD $MY_ARGS  ${FIXTURE_DIR}/${i}.json
done
