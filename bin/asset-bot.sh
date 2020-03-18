#!/bin/bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate bakuchi

HOMEDIR=${HOME}/repo/bakuchi

cd ${HOMEDIR}

inv bot-asset
