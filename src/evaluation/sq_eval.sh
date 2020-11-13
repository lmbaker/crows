#!/bin/bash

if [[ $# -ne 2 ]]; then
  echo "This script requires two parameters, a filepath to a directory and the suffix to the name of the benchmark predictions file (after 'benchmark_predictions' and before '.json')."
    exit 2
fi

DOCUMENTS_DIR=$1

BENCHMARK_PREDICTIONS_NAME=$2

python squad_eval.py -v ${DOCUMENTS_DIR}/benchmark.json ${DOCUMENTS_DIR}/benchmark_predictions${BENCHMARK_PREDICTIONS_NAME}.json -o ${DOCUMENTS_DIR}/squad_eval_metrics${BENCHMARK_PREDICTIONS_NAME}.json -p ${DOCUMENTS_DIR}
#python squad_eval.py -v ${DOCUMENTS_DIR}/benchmark.json ${DOCUMENTS_DIR}/benchmark_predictions_model_roberta-base-squad2.json -o ${DOCUMENTS_DIR}/squad_eval_metrics_model_roberta-base-squad2.json -p ${DOCUMENTS_DIR}
