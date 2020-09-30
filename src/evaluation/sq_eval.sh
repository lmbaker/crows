#!/bin/bash

if [[ $# -ne 1 ]]; then
    echo "This script requires one parameter, a filepath to a directory."
    exit 2
fi

DOCUMENTS_DIR=$1

python squad_eval.py -v ${DOCUMENTS_DIR}/benchmark.json ${DOCUMENTS_DIR}/benchmark_predictions.json -o ${DOCUMENTS_DIR}/squad_eval_metrics.json -p ${DOCUMENTS_DIR}
