# Terraform IaC Security Misconfiguration Dissertation

Working materials for Prashant Singh's AUT dissertation on evaluating LLM detection of security misconfigurations in Terraform AWS configurations.

## Contents

- `terragoat/`: TerraGoat Terraform corpus, Checkov and Trivy outputs, manually cross-referenced consensus data, notebooks, and figures
- `make_crosswalk.py`, `make_comparison.py`, `assemble_draft.py`: analysis and document-generation scripts

The consensus crosswalk is an analyst-produced candidate mapping and requires independent review.

The dissertation documents themselves are intentionally not included in this repository. `build_v05.py` and `thesis_*.py` generate the document from the result files and are kept as part of the record.

## LLM evaluation pipeline (run in this order)

1. `llm_evaluation.py`: sends the 14 TerraGoat files to Claude Sonnet 4.6, GPT-5.4 and Amazon Nova Pro through Amazon Bedrock; saves `responses/`. Needs `AWS_BEARER_TOKEN_BEDROCK` in the environment (never commit it).
2. `judge_findings.py`: blinded judge maps findings to Checkov/Trivy findings; saves `judgments/`.
3. `score_results.py`, `extra_stats.py`: precision, recall, F1, category scores, coverage, paired tests.
4. `remediation_judge.py`, `aggregate_remediation.py`: two-judge remediation scoring and agreement.
5. `validity_judge.py`: exploratory validity check of unmatched findings.
6. `make_figures_ch5.py`, `build_v05.py` (uses `thesis_text.py`, `thesis_data.py`): regenerate figures and the dissertation from the result files.

## Second dataset (generalisation check)

`collect_corpus.py` samples public GitHub repositories and Terraform Registry module repositories (seeded, manifest in `corpus_manifest.csv`), `scan_corpus.py` scans them with Checkov and Trivy, and `corpus_eval/` holds a copy of the pipeline scripts with the second dataset's inputs and results. `run_corpus_eval.sh` runs it end to end.

## Notes

- Model calls use Amazon Bedrock; set `AWS_BEARER_TOKEN_BEDROCK` in the environment. No credentials are stored in this repository.
- `terragoat/terraform/aws/` contains the deliberately vulnerable TerraGoat files (Apache 2.0, bridgecrewio/terragoat), including its fake example access keys.
- `Appendix E` evidence images in `terragoat/evidence_E*.png` are rendered from the saved logs, not screen captures.
