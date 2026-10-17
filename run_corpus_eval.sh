set -e
cd "$(dirname "$0")/corpus_eval"
python llm_evaluation.py --strategies zeroshot
python judge_findings.py
python score_results.py
python extra_stats.py
python remediation_judge.py
python aggregate_remediation.py
python validity_judge.py
python summarise_validity.py
echo CORPUS_DONE
