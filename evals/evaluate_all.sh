#!/bin/bash
# Evaluate all models on OneOS real environment
# Uses the OneOS venv which has assistant installed in dev mode
# Skips GRM (dense/slow) by default - use --include-dense to enable it

VENV_PYTHON="/home/waser/Projets/OneOS/src/.venv/bin/python3"
SCRIPT="/home/waser/Projets/OneOS/src/evals/model_compare_multiturn.py"
TRACE_BASE="/tmp/traces"

# MOE models only (grm is slow dense model, skipped by default)
MODELS="gemma ornith qwen"

for MODEL in $MODELS; do
    echo "=========================================="
    echo "Testing $MODEL..."
    echo "=========================================="
    $VENV_PYTHON "$SCRIPT" --model "$MODEL" --trace-dir "$TRACE_BASE/$MODEL"
    echo ""
done

# Optionally run GRM with --include-dense:
# $VENV_PYTHON "$SCRIPT" --model grm --trace-dir "$TRACE_BASE/grm"
