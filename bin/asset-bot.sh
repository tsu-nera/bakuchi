#!/bin/bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate bakuchi

EXECDIR=${HOME}/repo/bakuchi_production
SAVEDIR=${HOME}/repo/bakuchi

cd ${EXECDIR}

inv bot-asset

ASSET_FILE_FROM=${EXECDIR}/logs/cron/asset.log
ASSET_FILE_TO=${SAVEDIR}/logs/cron/asset.log

ASSET_FILE_FROM_COINCHECK=${EXECDIR}/data/assets/coincheck.csv
ASSET_FILE_TO_COINCHECK=${SAVEDIR}/data/assets/coincheck.csv

ASSET_FILE_FROM_LIQUID=${EXECDIR}/data/assets/liquid.csv
ASSET_FILE_TO_LIQUID=${SAVEDIR}/data/assets/liquid.csv

ASSET_FILE_FROM_TOTAL=${EXECDIR}/data/assets/total.csv
ASSET_FILE_TO_TOTAL=${SAVEDIR}/data/assets/total.csv

cp ${ASSET_FILE_FROM} ${ASSET_FILE_TO}
cp ${ASSET_FILE_FROM_COINCHECK} ${ASSET_FILE_TO_COINCHECK}
cp ${ASSET_FILE_FROM_LIQUID} ${ASSET_FILE_TO_LIQUID}
cp ${ASSET_FILE_FROM_TOTAL} ${ASSET_FILE_TO_TOTAL}
