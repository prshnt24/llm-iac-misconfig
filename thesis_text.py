"""Prose for the revised chapters. Every number comes from thesis_data, so text and results cannot drift apart."""
from thesis_data import *

cz, cf, gz, gf, nz, nf = RUNS[0], RUNS[1], RUNS[2], RUNS[3], RUNS[4], RUNS[5]
v = lambda r, k: S[r][k]
pv = lambda p: "p < .001" if float(p) < 0.001 else (f"p = {float(p):.3f}" if float(p) < 0.01 else f"p = {float(p):.2f}").replace("0.", ".")
pair = lambda a, b: PT[(a, b)]
unmatched_total = sum(int(VAL[r]["unmatched"]) for r in RUNS)
valid_total = sum(int(VAL[r]["valid"]) for r in RUNS)
debat_total = sum(int(VAL[r]["debatable"]) for r in RUNS)
invalid_total = sum(int(VAL[r]["invalid"]) for r in RUNS)
adj = [float(VAL[r]["adjusted_precision_valid"]) for r in RUNS]
prec_s = [float(v(r, "precision_strict")) for r in RUNS]
prec_l = [float(v(r, "precision_lenient")) for r in RUNS]
cov_pct = lambda r: pc(CV[r]["of_223"])
rem = lambda r: f2(REM[r]["mean_of_judges"])
share = lambda r, j: pc(REM[r][f"{j}_share_2"])

T = {}

T["abstract"] = (
    f"This dissertation tests how well large language models (LLMs) detect security misconfigurations in Terraform code for Amazon Web Services and how good "
    f"their repair advice is. Claude Sonnet 4.6, GPT-5.4 and Amazon Nova Pro, reached through Amazon Bedrock in place of the proposed GPT-4o and Gemini 2.5 Pro, "
    f"reviewed the 14 TerraGoat AWS files under zero-shot and few-shot prompting. The reference set is the {N_CONS} resource-level findings on which Checkov and "
    f"Trivy agree after a documented crosswalk of their policies, and a blinded judge model, audited by hand, matched model findings to it. Claude Sonnet 4.6 "
    f"scored highest, with recall of {f2(v(cz,'recall'))}, strict precision of {f2(v(cz,'precision_strict'))} and an F1-score of {f2(v(cz,'f1_strict'))} under zero-shot prompting. "
    f"GPT-5.4 reached {f2(v(gz,'f1_strict'))} to {f2(v(gf,'f1_strict'))} and Nova Pro {f2(v(nz,'f1_strict'))} to {f2(v(nf,'f1_strict'))}. Precision was similar across models, so recall separated them, and "
    f"few-shot prompting made no detectable difference. Which categories were detected well depended on the model, and GPT-5.4 and Nova Pro covered none of "
    f"the {RDS_TOTAL} findings in a file of repeated RDS cluster resources. Mean remediation scores for correctly detected issues were {rem(cz)}, {rem(gz)} to {rem(gf)} and "
    f"{rem(nz)} to {rem(nf)} on a 0 to 2 scale. On {C_N_FILES} further files from public repositories and registry modules, the ranking held but strict precision fell "
    f"to {f2(CS[CRUNS[2]]['precision_strict'])} to {f2(CS[CRUNS[0]]['precision_strict'])}, because the models reported many findings that the tools did not. The results rest on one main benchmark, an "
    f"analyst-built crosswalk, single runs and LLM-assisted judging."
)

T["scope"] = (
    'The empirical scope is Terraform HCL for AWS resources. TerraGoat provides a controlled primary dataset of 14 AWS Terraform files. A second dataset of 46 files, 30 from public GitHub repositories and 16 from Terraform Registry modules, is used as a generalisation check. It is smaller than the 100 to 200 repositories and 30 to 50 modules planned in the proposal (Section 3.2). The models evaluated are Claude Sonnet 4.6, GPT-5.4 and Amazon Nova Pro, each reached through Amazon Bedrock and each under zero-shot and few-shot prompting on TerraGoat and under zero-shot prompting on the second dataset. The proposal named GPT-4o and Gemini 2.5 Pro; neither was available through the access route used, and the substitution is described in Section 3.4.1. The temporal boundary is the set of models available in October 2026.'
)

T["structure"] = (
    "Chapter 2 reviews IaC security, static analysis, LLM-based code analysis, prompt design, the evaluation of LLM output, and the research gap. "
    "Chapter 3 describes the research design, datasets, construction of the reference set, prompts, matching and judging procedures, metrics, and threats "
    "to validity. Chapter 4 reports the Checkov results for TerraGoat AWS. Chapter 5 builds the cross-tool reference set, reports the model evaluation "
    "for each research question, and discusses the findings and their limits. Chapter 6 summarises the conclusions, contributions and limitations, and "
    "identifies future work."
)

# ---------------- Chapter 2 ----------------
T["iac_survey"] = (
    "Infrastructure as Code is the practice of defining and provisioning computing infrastructure through machine-readable configuration files, rather "
    "than through manual processes or interactive administration interfaces (Morris, 2021). The appeal is straightforward: teams can version-control their "
    "infrastructure, review changes before deployment, roll back to known states, and reproduce environments reliably across development, staging, and "
    "production. Industry surveys track this adoption. HashiCorp's 2023 State of Cloud Strategy Survey, run by Forrester with nearly 1,000 practitioners and decision "
    "makers, examined how organisations manage infrastructure across multiple clouds (HashiCorp, 2023). Research on IaC "
    "security began with script-level studies. Rahman et al. (2019) analysed 1,726 IaC scripts and identified seven recurring security smells, among them "
    "hard-coded secrets and default or empty passwords, which shows that insecure patterns were already widespread before Terraform became dominant."
)

T["model_para"] = (
    "LLMs are neural networks trained on large corpora of text and source code. They have demonstrated the ability to generate, explain, and review code "
    "across many programming languages and configuration formats (Hou et al., 2024). The models studied here are Claude Sonnet 4.6 from Anthropic (2026b), "
    "GPT-5.4 from OpenAI (2026), and Amazon Nova Pro (Amazon Artificial General Intelligence, 2025). They were chosen from the models that the researcher could "
    "reach through Amazon Bedrock (Amazon Web Services, 2026a) in October 2026, and they are not a ranking of the best models in existence. The LLM landscape "
    "changes quickly, and newer models will exist by the time this dissertation is read. The evaluation is therefore time-bounded to models accessible during "
    "the research period."
)

T["gap_hedge"] = (
    "To the author's knowledge, no published study has systematically evaluated LLM performance on Terraform HCL security misconfiguration detection using "
    "precision, recall, and F1-score as metrics, comparing multiple models and prompting strategies against a reference set built from static analysis tools. "
    "That is the gap this dissertation addresses."
)

T["sec_llm_sec"] = [
    "Evidence on LLMs in security-sensitive code tasks is mixed. Pearce et al. (2022) asked GitHub Copilot to complete 89 scenarios drawn from the MITRE "
    "list of high-risk weaknesses and found that roughly 40% of the 1,689 programs it produced were vulnerable. That study concerns code generation, whereas "
    "this dissertation concerns review of existing code, but it shows that fluent output cannot be assumed to be secure. For review tasks, Ullah et al. "
    "(2024) built a framework to test eight LLMs on vulnerability identification and reasoning. They reported non-deterministic answers, unfaithful "
    "reasoning, and results that changed after small edits to the code, and concluded that the models could not yet be relied on for this purpose. These "
    "findings justify two design choices made here: every response is saved so that results can be audited, and each condition is reported separately "
    "instead of being averaged into a single claim about LLM ability."
]

T["sec_eval"] = [
    "2.6 Measuring and Judging LLM Output",
    "A detection study needs a defined way to count correct and incorrect findings. Precision is the share of reported findings that are correct, recall is "
    "the share of known issues that are reported, and the F1-score is their harmonic mean (Powers, 2011). These measures depend on a reference set, and "
    "the quality of the reference set limits what the scores can mean. For LLM output, a further difficulty arises: models answer in free text, so each "
    "answer must be mapped to the reference items before it can be counted. Manual mapping is slow and itself subjective. A growing body of work uses a "
    "strong LLM as the judge. Zheng et al. (2023) found that a strong judge model agreed with human raters more than 80% of the time, about the same level "
    "as agreement between humans, while also documenting biases such as favouring its own style of answer and favouring longer answers. This literature "
    "supports using a judge model with safeguards: hiding which model wrote an answer, auditing a sample of decisions by hand, and checking agreement "
    "between more than one judge. Agreement between judges is commonly summarised with a weighted kappa, which Landis and Koch (1977) suggest reading as "
    "substantial between .61 and .80 and almost perfect above .80. The present study follows those practices and reports where they fall short.",
]

# ---------------- Chapter 3 ----------------
T["design_sentence"] = (
    "This research uses a quantitative empirical design, structured as a comparative evaluation experiment. A fixed corpus of Terraform configuration files "
    "is scanned by two static analysis tools and then submitted to three LLMs, and detection performance is measured using precision, recall, and F1-score. "
    "The same corpus, the same reference set, and the same metrics are applied to every model and prompting condition. Because the two static tools define "
    "the reference set, they are compared with the models through coverage rather than accuracy (Section 3.5). An experiment was chosen over a case study of one team's practice "
    "(Runeson & Höst, 2009) because the question is about measurable differences between models under controlled inputs, and over a purely qualitative "
    "review of model answers because RQ1 and RQ2 ask for quantities that can be compared. The design follows the evaluation logic of design science, in "
    "which an artefact, here an LLM-based reviewer of Terraform, is assessed against stated criteria (Hevner et al., 2004), and threats to validity are "
    "grouped using the scheme in Wohlin et al. (2012)."
)

T["gh_note"] = (
    'A second dataset of real-world Terraform was collected through the GitHub REST API. The search required language HCL, the terraform topic, at least five stars, a last push after 1 January 2023, and aws in the repository name or description. Forks, archived repositories, the terraform-aws-modules organisation (used separately below) and repositories whose names suggest deliberately vulnerable projects were removed. The remaining repositories from the first 200 results in star order were shuffled with a fixed random seed, cloned at depth one, and one AWS .tf file with at least two aws resources and between 800 and 10,000 bytes was drawn at random from each, until 30 files from 30 repositories had been obtained. The sample is smaller than the 100 to 200 repositories planned in the proposal, because every file also had to be scanned, judged and scored, and one file per repository was taken so that no project dominates. The repository, commit, original path and licence of every file are recorded in corpus_manifest.csv.'
)

T["reg_note"] = (
    'Sixteen root files from modules published by the terraform-aws-modules organisation, a widely used source of AWS modules for the Terraform Registry, were taken as a validation set. These modules are intended for production use and have been reviewed by many contributors, so they test whether tools and models produce excessive false positives on broadly accepted configurations. For each module, the root .tf file with the most aws resources was used, first among files of 800 to 10,000 bytes and then, in a second pass for modules whose root files were all larger, among files of up to 20,000 bytes, because module root files are larger than typical repository files. The set is smaller than the 30 to 50 modules planned, and all of the modules come from one maintaining organisation, which limits what it can say about the Registry as a whole.'
)

T["ground_truth"] = (
    "A reference set is needed because a model answer cannot be called right or wrong without something to compare it with. No expert-labelled benchmark "
    "exists for the TerraGoat AWS files, and labelling all of their resources by hand was outside the scope of a single-student project. The reference set "
    "was therefore built from two independent static analysis tools. Checkov v3.3.9 and Trivy 0.73.0 were run against the 14 files, and a finding was kept "
    "only when both tools reported the same weakness on the same resource block in the same file. Requiring agreement removes findings that only one tool "
    "reports, which are more likely to reflect that tool's rule quirks. The two tools use different identifiers, so identical identifier numbers cannot be "
    "matched directly: Trivy uses Aqua identifiers such as AWS-0028, while Checkov uses identifiers such as CKV_AWS_28. An analyst-built crosswalk "
    "links 41 Trivy policies to the Checkov policies that describe the same control (Appendix C), and several Trivy records that map to one Checkov policy "
    "on one resource are grouped into a single finding. The result is "
    f"{N_CONS} consensus findings. A further {N_CHK_ONLY} findings were reported only by Checkov and {N_TRV_ONLY} only by Trivy. The consensus set is used as the "
    "reference for strict scoring, and the full set of "
    f"{N_ALL} findings is used for lenient scoring and for the coverage analysis. Each finding is also assigned to a misconfiguration category by keyword rules applied to the check name, as in Chapter 4; the rules are listed in Appendix D. "
    "The reference set is a convenient and documented benchmark, not an expert gold standard. The crosswalk was prepared by one analyst and has not been reviewed by a second security reviewer, which is a limitation "
    "discussed in Section 3.6."
)

T["models"] = (
    "Three models were evaluated: Claude Sonnet 4.6 (Anthropic), GPT-5.4 (OpenAI) and Amazon Nova Pro (Amazon). All were called through the Amazon Bedrock "
    "Converse interface in the Asia Pacific (Sydney) region, using the inference profiles au.anthropic.claude-sonnet-4-6, global.openai.gpt-5.4 and "
    "apac.amazon.nova-pro-v1:0. The proposal named GPT-4o and Gemini 2.5 Pro. Neither was available through the account the researcher had, and obtaining "
    "separate provider accounts and keys would have delayed the work beyond the submission date. Claude Sonnet 4.6 was retained as proposed. GPT-5.4 replaces "
    "GPT-4o as the OpenAI model and is a later and probably stronger model, which means the comparison cannot be read as a test of GPT-4o. Amazon Nova Pro "
    "replaces Gemini 2.5 Pro and is a different class of model, so the study includes one strong and one lower-capability alternative. The substitution "
    "changes which models the conclusions describe and is a limitation of the work. Temperature was set to 0 for Claude Sonnet 4.6 and Nova Pro. GPT-5.4 "
    "rejects the temperature parameter on Bedrock, so its default sampling was used, and repeat runs of that model could differ. The maximum output length was "
    "16,000 tokens for Claude and GPT-5.4 and 9,000 for Nova Pro, whose limit is 10,000. Each model-prompt-file combination was run once, giving 84 requests "
    f"between {FIRST[:10]} and {LAST[:10]}."
)

T["prompts"] = (
    "Two prompt strategies were evaluated. In the zero-shot condition, each configuration file is submitted with an instruction to identify all security "
    "misconfigurations and to give, for each, the Terraform resource address, the name of the issue, the risk, and a specific remediation. The answer is "
    "requested as a JSON array so that it can be processed without guessing where one finding ends. In the few-shot condition, the same instruction is "
    "followed by two worked examples before the target file: one IAM over-permissioning finding and one missing S3 public access block. The two prompts "
    "differ only by those examples, and both are identical across the three models. The full text is given in Appendix B. The instruction was changed from "
    "the free-text list in the original plan to a JSON array, because free-text lists cannot be matched to resources reliably. "
    "Chain-of-thought prompting was not tested; it is left to future work because it raises the cost of every call and changes the comparison from "
    "examples against no examples to a different kind of intervention."
)

T["matching"] = [
    "Each model answer was saved in full, and its findings were then mapped to the tool findings by a judge model. The judge was GPT-5.4. For each model "
    "answer for each file, it received the findings with no indication of which model or prompt produced them, together with every Checkov and Trivy "
    "finding for that file (status hidden), and returned for each finding the identifiers of the tool findings that describe the same weakness on the same "
    "resource, or none. A model finding counts as a strict hit if it matches at least one consensus finding, and as a lenient hit if it matches any tool "
    "finding. Findings with no match are counted as false positives under the strict rule. The judge prompt is reproduced in Appendix D.",
    "A judge model replaced the keyword matching that had first been used. In a first scoring pass, keyword overlap credited a finding about plaintext "
    "credentials in user data to the check for the instance metadata service, and rejected clear findings such as disabled backups, so that approach was "
    "dropped. The judge was then audited by hand. A random sample of 52 judge decisions, 22 matches and 30 rejections, was read against the "
    "Terraform source and the tool findings, with the help of the AI coding assistant described in Section 3.8, and no errors were found in the sample. This does not show that the judge is error-free, but it bounds the "
    "likely error rate for a sample of that size and gives some confidence in the conclusions. GPT-5.4 is also one of the models being evaluated. The "
    "judge could not see which model wrote an answer, which reduces the risk of favouring its own output but does not remove it (Zheng et al., 2023).",
    "Findings that matched no tool finding were examined in an exploratory step. The same judge read the Terraform file and labelled each unmatched "
    "finding as valid, arguable, or invalid. About 20 of these labels, including all seven labelled invalid on TerraGoat, were read as a check, and two of the invalid labels were confirmed against "
    "the source. These labels are used only to qualify the precision figures and not to alter them. Remediation advice was "
    "scored on the three-point rubric by two judges, GPT-5.4 (OpenAI, 2026) and Claude Sonnet 5.5 (Anthropic, 2026a), working independently and blind to the source model. The reference fix for "
    "each item is the standard correction for the matched tool check, which the judge assessed with the Terraform source in view. Both judges "
    "scored the same items so that agreement could be reported."
]

T["metrics"] = (
    "Four quantities are reported for each model and prompt. Strict precision is the number of findings that match a consensus finding divided by the "
    "number of findings the model reported. Lenient precision is the same ratio, counting a match with any Checkov or Trivy finding. Recall is the number "
    f"of distinct consensus findings covered by at least one model finding divided by {N_CONS}. The F1-score is the harmonic mean of precision and recall "
    "(Powers, 2011), reported for both precision variants. Several model findings may cover the same reference finding, and one finding can cover "
    "several, so precision is computed over model findings and recall over reference findings. Category-level recall, precision and F1-score "
    "use the same definitions within each category assigned as described in Section 3.3. Checkov and Trivy cannot be scored against "
    "the consensus set, since a finding is in the set only because both of them report it, so their recall is 1.00 by construction. They are "
    f"compared with the models through coverage: the share of the {N_ALL} findings that either tool reports which a model also reports. "
    "Differences between conditions are tested with an exact test on the consensus findings that one condition covers and the other does not, which "
    "is equivalent to McNemar's test. Remediation quality is the mean rubric score, the share of items scoring 2, and the quadratic-weighted kappa between the "
    "two judges. With 75 reference findings, a single run per condition and a single repository, the tests indicate how large an observed "
    "difference is relative to chance and do not support generalisation beyond this benchmark."
)

T["threats"] = [
    "Several threats to validity affect the results. The first is construct validity of the reference set. The set is defined by two static tools, "
    "so a model that correctly reports an issue neither tool reports is scored as wrong, and a weakness that both tools miss cannot be recovered. The "
    "crosswalk that aligns the tools was prepared by one analyst and has not been independently reviewed. Strict precision is therefore a lower bound, "
    "and the study reports lenient precision and an exploratory validity check to show the size of the effect.",
    "The second threat is the judge. Matching and remediation scoring were done by LLMs, which may be inconsistent or biased. The judges were blind to "
    "the source model, the matching judge was audited on a sample of 52 decisions, and the remediation judges were compared with each other, but the "
    "audit was not independent and the sample was small. The third threat is model selection. The models differ from the proposal, one of them cannot be "
    "run at temperature 0, and each condition was run only once, so run-to-run variation is not measured. The fourth is data contamination. TerraGoat is a "
    "public repository that is widely used for demonstrating scanners, and its files may appear in model training data, which could raise detection rates "
    "above what would be seen on unfamiliar code. The public repositories in the second dataset may also be in the training data. The fifth is scope. The main results come from 14 files of one deliberately vulnerable AWS project. A second dataset of "
    + str(C_N_FILES) + " files from public repositories and registry modules gives a limited check, but it holds only " + str(C_N_CONS) + " reference findings and one file was "
    "drawn per repository, so the results cannot be generalised to production repositories, to other clouds, or to larger files. The sixth is the use of the JSON output format, which "
    "differs from the proposed free-text list and may favour models that follow output instructions closely. Categories were assigned by keyword rules "
    "applied to the check names, and some categories contain very few findings, so category-level figures are indicative only."
]

T["avail"] = (
    "The scripts, raw model responses, judge outputs, scored result files and figures are held in the project folder and will be placed in a public GitHub "
    "repository on submission. The repository location will be confirmed with the supervisor before final submission. Appendix D lists the files. The API "
    "key used to reach Amazon Bedrock is not stored in the repository."
)

T["ai_decl"] = [
    "3.8 Use of Generative AI",
    "Generative AI tools were used in three ways in this work. First, the three LLMs described in Section 3.4.1 are the objects of study. Second, LLMs "
    "acted as judges for matching findings and scoring remediation advice, as described in Section 3.4.3. Third, an AI coding assistant, Claude Code, was "
    "used to help write the analysis scripts and to draft and revise parts of the text. The author is responsible for the content of the dissertation "
    "and for checking it against the underlying data and sources, and the use of these tools is declared in line with the university's expectations.",
]

# ---------------- Chapter 4 fixes ----------------
T["ch4_overview_tail"] = (
    "These results are the starting point for the reference set used in Chapter 5, where the Trivy results are added and the two tools are compared "
    "to form the consensus findings against which the models are scored."
)
T["ch4_next_head"] = "4.8 Link to the Model Evaluation"
T["ch4_next"] = (
    "The Checkov results above supply most of the findings in the reference set and show where the vulnerable configuration is concentrated. Chapter 5 adds "
    "the Trivy scan, aligns the two tools to produce the consensus findings, and then reports how the three models performed against them."
)

# ---------------- Chapter 5 ----------------
T["c5_intro"] = (
    "This chapter reports the static analysis comparison and the evaluation of the three LLMs. Checkov and Trivy outputs are available for the 14-file "
    "Terraform module. Their policy namespaces are not numerically interchangeable, so a manual semantic crosswalk was used to align them, producing the "
    f"{N_CONS} consensus findings that form the reference set (Section 5.2). Section 5.3 answers RQ1 with precision, recall and F1-score for each model and "
    "prompt, and compares the models with the tools through coverage. Section 5.4 answers RQ2 by category. Section 5.5 answers RQ3 with the remediation scores. "
    "Section 5.6 tests whether the findings hold on a second dataset of public repositories and registry modules. Section 5.7 discusses the results, and Section 5.8 sets out the limitations. All model figures come from one run per condition."
)

T["c5_cat_para"] = (
    "The " + str(N_CONS) + " consensus findings are concentrated in " + ", ".join(
        f"{c['category'].lower()} ({c['consensus_groups']})" for c in CATSUM[:-1]) + f", and {CATSUM[-1]['category'].lower()} ({CATSUM[-1]['consensus_groups']}). "
    "Categories were assigned from the check names using the rules described in Section 3.3, applied here to the consensus findings only and with the resource name added as an input to separate S3 findings, which is why "
    "these counts differ slightly from the Checkov-wide categories in Chapter 4. IAM over-permissioning has no consensus findings, because the tools "
    "agreed on only one IAM finding and it was assigned to another category by the name-based rules. These figures describe the composition of the "
    "analyst-adjudicated reference set. They are not model detection scores and should not be read as prevalence estimates for production Terraform."
)

T["rq1_h"] = "5.3 RQ1: Overall Detection Accuracy"
T["rq1"] = [
    f"Table 5.4 reports detection performance against the {N_CONS} consensus findings. Claude Sonnet 4.6 under zero-shot prompting had the highest "
    f"F1-score ({f2(v(cz,'f1_strict'))}). It reported {v(cz,'findings')} findings, {v(cz,'strict_hits')} of which matched a consensus finding, and it covered "
    f"{v(cz,'consensus_covered')} of the {N_CONS} reference findings. GPT-5.4 reached F1-scores of {f2(v(gz,'f1_strict'))} (zero-shot) and {f2(v(gf,'f1_strict'))} "
    f"(few-shot), and Amazon Nova Pro {f2(v(nz,'f1_strict'))} and {f2(v(nf,'f1_strict'))}.",
    f"Strict precision was similar across models, between {f2(min(prec_s))} and {f2(max(prec_s))}, so recall explains the ranking. Claude covered "
    f"{v(cz,'consensus_covered')} reference findings in the zero-shot run, GPT-5.4 {v(gz,'consensus_covered')} and Nova Pro {v(nz,'consensus_covered')}. The exact test shows how one-sided this is. "
    f"Of the reference findings that separated Claude from GPT-5.4 under zero-shot prompting, {pair(cz,gz)['only_a']} were found only by Claude and "
    f"{pair(cz,gz)['only_b']} only by GPT-5.4 ({pv(pair(cz,gz)['p_exact'])}). Between GPT-5.4 and Nova Pro, {pair(gz,nz)['only_a']} were found only by GPT-5.4 and "
    f"{pair(gz,nz)['only_b']} only by Nova Pro ({pv(pair(gz,nz)['p_exact'])}). Claude's findings contained nearly everything the other two found.",
    f"Much of the gap comes from one file. The file rds.tf holds {RDS_TOTAL} of the {N_CONS} reference findings, spread over nine near-identical Aurora "
    f"cluster blocks. Claude covered {RDS_COV[cz]} of them in the zero-shot run. GPT-5.4 reported {FINDINGS_RDS[gz]} finding for the whole file and Nova Pro "
    f"{FINDINGS_RDS[nz]}, and neither covered any of the {RDS_TOTAL}. Without rds.tf, zero-shot recall was {f2(NORDS_RECALL[cz])} for Claude, "
    f"{f2(NORDS_RECALL[gz])} for GPT-5.4 and {f2(NORDS_RECALL[nz])} for Nova Pro. The ordering of the models is unchanged, but the distance between "
    "Claude and GPT-5.4 shrinks considerably. Whether the two weaker models treated the repeated blocks as duplicates or simply stopped early was not tested.",
    f"The strict precision figures are low for every model. Strict scoring counts a finding as wrong when it matches a tool finding that only one tool "
    f"reported. Under the lenient rule, which accepts a match with any Checkov or Trivy finding, precision rose to between {f2(min(prec_l))} and "
    f"{f2(max(prec_l))}, and the lenient F1-score reached {f2(v(cz,'f1_lenient'))} for Claude zero-shot and {f2(v(cf,'f1_lenient'))} for Claude few-shot. "
    f"A third view is the exploratory validity check. Of the {unmatched_total} findings across all six runs that matched no tool finding, the judge "
    f"labelled {valid_total} valid, {debat_total} arguable and {invalid_total} invalid. Adding the valid findings to the matched ones gives an adjusted "
    f"precision of {f2(min(adj))} to {f2(max(adj))} (Table 5.6). Two examples show what the tools missed. Five of the six runs reported plaintext database "
    "credentials in the user data of aws_instance.db_app, and five of six reported a wildcard access policy on the Elasticsearch domain. Neither tool "
    "reported either issue. The adjusted figures depend on a single judge and on about 20 labels read in a manual check, and are offered as an indication "
    "of direction and not as a result.",
    f"Few-shot prompting did not change results in a way the data can distinguish from chance. Claude's strict F1-score moved from {f2(v(cz,'f1_strict'))} to "
    f"{f2(v(cf,'f1_strict'))}, GPT-5.4's from {f2(v(gz,'f1_strict'))} to {f2(v(gf,'f1_strict'))}, and Nova Pro's from {f2(v(nz,'f1_strict'))} to {f2(v(nf,'f1_strict'))}. "
    f"The exact tests on covered reference findings gave {pv(pair(cz,cf)['p_exact'])} for Claude and {pv(pair(gz,gf)['p_exact'])} for GPT-5.4, and Nova Pro "
    f"had no differing findings. The examples did change Claude's behaviour. It reported {v(cf,'findings')} findings against {v(cz,'findings')} and matched "
    f"{CV[cf]['all_tool_rows_covered']} of the {N_ALL} tool findings against {CV[cz]['all_tool_rows_covered']}, so the examples widened what it reported without "
    "adding reference findings, which lowered its strict precision.",
]

T["rq1_cov"] = (
    f"The static tools cannot be scored as the models were. The consensus set contains only findings that both tools report, so each tool has a recall of "
    "1.00 on it by construction, and any precision or F1-score for the tools would be circular. The comparison with Checkov and Trivy is therefore a "
    f"comparison of coverage (Table 5.5). Claude matched {CV[cz]['all_tool_rows_covered']} of the {N_ALL} findings reported by either tool in the zero-shot run "
    f"({cov_pct(cz)}) and {CV[cf]['all_tool_rows_covered']} ({cov_pct(cf)}) in the few-shot run, including {CV[cf]['checkov_only_covered']} of the {N_CHK_ONLY} reported only by "
    f"Checkov and {CV[cf]['trivy_only_covered']} of the {N_TRV_ONLY} reported only by Trivy in the few-shot run. GPT-5.4 matched {cov_pct(gz)} and {cov_pct(gf)} and "
    f"Nova Pro {cov_pct(nz)} and {cov_pct(nf)}. On this benchmark, then, the strongest model reproduces about half to three-fifths of what the two tools find, "
    "and the others a quarter or less, while also reporting issues the tools do not."
)

T["rq2_h"] = "5.4 RQ2: Category-Level Analysis"
T["rq2"] = [
    f"Table 5.7 and Figure 5.4 show recall by category. The one hardcoded-secret finding, the plaintext credentials in the user data of aws_instance.web_host, was found in all six runs. "
    f"Storage configuration recall ranged from {f2(min(cat(r,'Storage Configuration','recall') for r in RUNS))} to {f2(max(cat(r,'Storage Configuration','recall') for r in RUNS))}, "
    f"and publicly exposed storage was covered completely by Claude in both conditions. Claude also covered all {gt_n('Availability & Resilience')} availability and resilience findings and "
    f"{f2(cat(cz,'Encryption at Rest','recall'))} of the {gt_n('Encryption at Rest')} encryption findings, while GPT-5.4 and Nova Pro covered none of the availability findings and "
    f"between {f2(min(cat(r,'Encryption at Rest','recall') for r in RUNS[2:]))} and {f2(max(cat(r,'Encryption at Rest','recall') for r in RUNS[2:]))} of the encryption findings. "
    "Most of that difference is the RDS cluster file described in Section 5.3, which holds nine of the ten availability findings and nine of the twenty encryption findings.",
    f"The weakest categories were network exposure, logging and monitoring, and the residual category. Network exposure recall was {f2(cat(cz,'Network Exposure','recall'))} for Claude, "
    f"{f2(cat(gz,'Network Exposure','recall'))} and {f2(cat(gf,'Network Exposure','recall'))} for GPT-5.4, and {f2(cat(nz,'Network Exposure','recall'))} for Nova Pro. Claude's misses in this category were "
    f"four checks that a security group or rule has a description and the public endpoint of the EKS cluster. The description checks are documentation rules and "
    "a reviewer could reasonably leave them out. Logging and monitoring contains four findings, of which Claude found three and GPT-5.4 at most one. Because "
    "the categories hold between 1 and 20 findings, a single finding moves recall by 5 to 100 points, and these figures are indicative and not stable estimates.",
    f"The second part of RQ2 asks whether few-shot prompting improves the weaker categories. In this data it did not. Few-shot prompting left Claude's recall for network "
    f"exposure and for logging unchanged, lowered GPT-5.4's recall for network exposure from {f2(cat(gz,'Network Exposure','recall'))} to {f2(cat(gf,'Network Exposure','recall'))} and for logging from "
    f"{f2(cat(gz,'Logging & Monitoring','recall'))} to {f2(cat(gf,'Logging & Monitoring','recall'))}, and left Nova Pro unchanged. The single clear gain was GPT-5.4's recall for publicly exposed storage, which rose from "
    f"{f2(cat(gz,'Publicly Exposed Storage','recall'))} to {f2(cat(gf,'Publicly Exposed Storage','recall'))}. One of the two few-shot examples concerned a missing S3 public access block, so this gain probably reflects "
    "closeness to the example and not a general improvement in the category. Category-level precision and F1-scores are in Appendix D.",
]

T["rq3_h"] = "5.5 RQ3: Remediation Quality"
T["rq3"] = [
    f"Remediation advice was scored for the findings that matched a consensus finding, {sum(int(REM[r]['scored_findings']) for r in RUNS)} items across the six runs. Table 5.8 shows the "
    f"results. Claude's advice was almost always correct and specific, with a mean score of {rem(cz)} and {rem(cf)} and {share(cz,'gpt54')} of items scoring 2 under the first judge in the zero-shot run. GPT-5.4's mean was "
    f"{rem(gz)} and {rem(gf)}, and Nova Pro's {rem(nz)} and {rem(nf)}, with only about half of its items scoring 2. The two judges gave the same score to "
    f"{pc(AGREE['exact'])} of the {AGREE['n']} items, never differed by more than one point, and had a quadratic-weighted kappa of {AGREE['kappa']:.2f}, which falls in the almost perfect band "
    "of Landis and Koch (1977). Two items could not be scored by both judges because one judge's output could not be read, and they are left out.",
    "These scores carry two qualifications. Remediation was scored only where the detection was correct, so a model that detects less is scored on fewer, "
    "and probably easier, items. A model with low recall can therefore look good on remediation. Claude's means are also close to the maximum of 2, which leaves little room to separate "
    "zero-shot from few-shot, and the differences between the two strategies within a model, at most 0.05, are within what judge noise would produce.",
    "The lower scores had a recognisable form. For IAM wildcard policies and open egress rules, the weaker models gave advice in the right direction "
    "without a concrete replacement, for example to restrict the policy to the necessary actions and resources or to limit egress to specific destinations. "
    "Both judges scored that as partial. In one case Nova Pro advised setting the bucket ACL to private to deal with a missing public access block, which does not satisfy "
    "the check, and in another GPT-5.4 proposed default S3 encryption where the check requires a customer-managed key. These are the kinds of errors a reviewer "
    "would catch, but they would mislead someone applying the advice directly.",
]

T["disc_h"] = "5.7 Discussion"
T["disc"] = [
    "The main result is the size of the gap between models and the absence of a gap between prompts. Under the same instruction, Claude Sonnet 4.6 "
    "covered more than twice as many reference findings as GPT-5.4 and three times as many as Nova Pro, and adding two examples changed none of the "
    "models by an amount the data can separate from noise. This agrees with the caution in Ullah et al. (2024) that LLM performance on security review "
    "differs widely between models and cannot be assumed. It is also consistent with Munshi et al. (2025), who found clear differences between models in "
    "threat identification on AWS scenarios, although their task, threat modelling over architecture descriptions, differs from the review of Terraform "
    "resources studied here, so the two results are not directly comparable.",
    "The results suggest that LLMs and static tools find overlapping but different sets of issues. The tools themselves agree on only a minority of what "
    f"they report: {N_CONS} of {N_ALL} findings, about a third, are shared. The strongest model reproduced about half to three-fifths of what either tool reports, "
    "and in addition reported plaintext credentials in the user data of a database host and a wildcard policy on an Elasticsearch domain, which neither tool flagged. "
    "A tool-based reference set therefore has two effects. It makes the study repeatable, and it measures models against the tools' blind spots as well as "
    "their strengths. The results favour using a strong LLM as a second reviewer next to Checkov and Trivy, not in place of them: the tools "
    "give repeatable results at low cost, and the model adds breadth and readable advice. Any such use needs a human reader, since both strict precision "
    "and the invalid findings show that the model also raises concerns that are not real.",
    "Why the models differ cannot be settled from this data. GPT-5.4 and Nova Pro produced much shorter answers, "
    f"{v(gz,'findings')} and {v(nz,'findings')} findings in total against {v(cz,'findings')} for Claude, and their recall deficit is concentrated in the file with repeated "
    "resources. A prompt that required every resource to be reviewed separately might raise their recall. That is a hypothesis for later work and was not tested here. "
    "The size of the effect also cannot be separated from the possibility that TerraGoat is part of some models' training data, which would favour models that "
    "had seen it. A further caution concerns the two judging roles, since GPT-5.4 both wrote answers and matched them. The matching was blind and the sample audit found "
    "no errors, but a study with a judge from a model family outside the evaluation would remove the concern.",
]

T["lim_h"] = "5.8 Limitations"
T["lim"] = (
    "The limitations follow the threats set out in Chapter 3. The main evidence comes from one deliberately vulnerable AWS repository whose files may be known to "
    "the models. The second dataset is small, yields only " + str(C_N_CONS) + " reference findings, and consists of public code that the models may also have seen, so neither "
    "dataset supports general claims about production repositories or other clouds. The reference "
    "set depends on two static tools and a crosswalk made by one analyst without independent review, and strict precision is a lower bound. Matching and remediation "
    "scoring relied on LLM judges, audited on a small sample that was not independent. The models differ from the proposal, one of them could not be run at temperature 0, "
    "and each condition was run once, so run-to-run variation is unknown. Category results rest on between 1 and 20 findings each. None of these limitations changes the descriptive results reported above, but together they mean that the "
    "figures should be read as a documented comparison on one benchmark and not as general estimates of model ability."
)

# ---------------- Chapter 6 ----------------
T["c6"] = {
    "6.1 Summary of Findings": [
        f"RQ1 asked how accurately LLMs detect Terraform misconfigurations compared with Checkov and Trivy. On the TerraGoat AWS module, Claude Sonnet 4.6 "
        f"was the most accurate model, with an F1-score of {f2(v(cz,'f1_strict'))} under zero-shot prompting, recall of {f2(v(cz,'recall'))} and strict precision of "
        f"{f2(v(cz,'precision_strict'))}. GPT-5.4 reached {f2(v(gz,'f1_strict'))} to {f2(v(gf,'f1_strict'))} and Amazon Nova Pro {f2(v(nz,'f1_strict'))} to {f2(v(nf,'f1_strict'))}. Precision was similar across the models and recall "
        f"separated them. The tools could not be scored against a reference set they define, so the comparison is one of coverage: the strongest model "
        f"matched {cov_pct(cz)} to {cov_pct(cf)} of the findings that either tool reports and also raised valid issues that neither tool reported.",
        f"RQ2 asked which categories LLMs identify most and least effectively, and whether few-shot prompting helps the weaker ones. Which categories were strongest depended on the model. "
        f"Storage configuration and the single hardcoded-secret finding were covered well by all three models, while public storage exposure, availability and "
        f"encryption were strong only for Claude, and for GPT-5.4 on public storage only with few-shot prompting. Network exposure was the weakest category for all "
        f"three, and logging was weak for GPT-5.4 and Nova Pro. Few-shot prompting did not improve the weaker categories. The only clear gain, for GPT-5.4 on publicly exposed storage, coincides with an example about that category.",
        f"RQ3 asked how well the remediation advice matches expert-defined fixes. For correctly detected issues, Claude's advice scored {rem(cz)} on the 0 to 2 rubric, GPT-5.4's "
        f"{rem(gz)} to {rem(gf)} and Nova Pro's {rem(nz)} to {rem(nf)}. Two judges agreed closely (kappa {AGREE['kappa']:.2f}). The weaker models more often gave advice that was in the right direction but "
        "too general to apply, and occasionally advice that would not satisfy the check.",
    ],
    "6.2 Contributions": [
        "The study contributes an evaluation design at resource-block level that separates a strict reference set, built from the agreement of two static "
        "tools, from the wider set of tool findings, and that reports precision under both. It contributes a documented crosswalk between Trivy and Checkov "
        "policy identifiers for AWS Terraform, and the finding that identifiers cannot be equated by their numeric suffix. It contributes a comparison of three "
        "LLMs under zero-shot and few-shot prompting, with saved raw responses, judge outputs and scoring scripts that allow every figure to be reproduced and "
        "challenged. It also records two methodological lessons. Keyword matching of free-text findings to policy names misclassified findings in both "
        "directions and was replaced by a blinded and audited judge. Scoring tools against a reference set that they define is circular, so coverage "
        "is the fairer basis for comparing them with models.",
    ],
    "6.3 Limitations": [
        "The main results rest on one intentionally vulnerable AWS repository that may be present in the models' training data. The reference set depends on two "
        "static tools and an analyst crosswalk that has not been independently reviewed. Matching and remediation scoring used LLM judges that were audited on a "
        "small sample. The models differ from those in the proposal, GPT-5.4 could not be run at temperature 0, and each condition was run once. The second dataset "
        "is small and yields only " + str(C_N_CONS) + " reference findings. The findings should therefore be treated as a documented comparison on one "
        "benchmark, not as a general ranking of the models.",
    ],
    "6.4 Future Work": [
        "The first priority is to scale the second dataset to the 100 to 200 repositories and 30 to 50 modules planned in the proposal, with several files per "
        "repository, and to repeat each condition several times to measure run-to-run variation. A second security reviewer should adjudicate the policy crosswalk and a sample of the judge decisions, and a judge from a model family "
        "outside the evaluation should be used. The evaluation should be repeated with GPT-4o and Gemini 2.5 Pro, as originally proposed, to see whether "
        "the ranking holds. Prompts that require each resource to be reviewed separately could be tested to see whether they close the recall gap on repeated resources, and "
        "chain-of-thought prompting, Azure and Google Cloud configurations, and integration into continuous integration pipelines are natural extensions. "
        "Any extension should keep the distinction between a strict reference set and the broader set of tool findings, and should add a small expert-labelled "
        "sample, so that precision can be estimated without depending on the tools.",
    ],
    "6.5 Closing Statement": [
        "On the TerraGoat benchmark, the choice of model mattered far more than the choice of prompt. The strongest model found most of what two static "
        "scanners agree on, gave advice that was almost always correct, and raised valid concerns that the scanners missed, while the weaker models found "
        "about half or less and gave less precise advice. The evidence supports using a strong LLM as a reviewer alongside static tools. It does not support replacing "
        "the tools, and the check on public repositories shows that agreement with the tools is far lower on production-style code, so the results do not carry over directly.",
    ],
}


T["lit_iac_research"] = (
    "Later work widened the view. A systematic mapping study of 31 IaC publications found that more than half proposed a framework or tool, which suggests "
    "that early research concentrated on building IaC tooling more than on measuring how secure the resulting code is (Rahman et al., 2018). GLITCH "
    "(Saavedra & Ferreira, 2022) replaced single-technology smell detectors with one framework covering Puppet, Ansible and Chef and "
    "reported higher precision and recall than earlier tools, but it still applies hand-written rules, so what it can find is limited to what its authors "
    "encoded. Verdet et al. (2025) measured the adoption of Terraform security practices across 812 GitHub projects using static analysis and found that "
    "access policies were the most widely adopted practice and encryption at rest the most neglected, with a positive correlation between a repository's star "
    "count and its adoption of the practices. Two points follow for the present study. Encryption at rest is also the largest group of failures in "
    "TerraGoat (Chapter 4), so the empirical literature and the benchmark agree on where weaknesses cluster. And these studies use rule-based static analysis as "
    "the measuring instrument without asking how far two such instruments agree with each other, or whether a model could act as a different instrument. "
    "The low agreement between Checkov and Trivy reported in Chapter 5 shows why that question matters."
)

T["lit_iac_eval"] = (
    "A second Terraform-related benchmark concerns generation. IaC-Eval (Kon et al., 2024) contains 458 human-curated scenarios for popular AWS services and "
    "checks whether generated programs meet the stated intent. The best model it tested, GPT-4, passed 19.36% of scenarios at the first attempt, against 86.6% "
    "for the same model on a general Python benchmark. Writing a correct configuration from a description is a different task from reading one, so these "
    "figures cannot be carried over to detection. They do show that the cloud-specific knowledge needed for IaC is a weak point of general-purpose models, "
    "which makes it reasonable to test their review ability and not to assume it."
)

T["lit_validity"] = (
    "Two cautions from the wider LLM research literature shape the design. Sallou et al. (2024) argue that research using LLMs in software engineering is "
    "exposed to closed-source models whose versions can change, to leakage between training data and evaluation material, and to results that are hard to "
    "reproduce. The present study responds in part: it records model identifiers, region and dates, saves every response, and adds a second set of files "
    "drawn at random from public repositories and registry modules. It cannot inspect the models' training data, so leakage remains a threat. Sokolova and "
    "Lapalme (2009) showed that performance measures respond differently to changes in the confusion matrix, which is why this study reports strict and "
    "lenient precision, recall and F1-score together and not a single figure. For ordinal ratings such as the remediation rubric, weighted kappa gives "
    "partial credit for near agreement (Cohen, 1968)."
)

T["lit_synthesis"] = (
    "These studies leave three gaps. Security research on IaC measures prevalence or adoption with static tools but does not examine whether "
    "the tools agree with each other (Rahman et al., 2019; Saavedra & Ferreira, 2022; Verdet et al., 2025). Work on LLMs for infrastructure either "
    "generates IaC (Kon et al., 2024), detects code smells (Vo et al., 2025) or models threats at architecture level (Munshi et al., 2025), so none tests "
    "misconfiguration detection at resource level. And studies of LLMs on security-sensitive code report unreliable and model-dependent behaviour (Pearce "
    "et al., 2022; Ullah et al., 2024) without a repeatable, resource-level reference set for Terraform. This dissertation addresses the three gaps "
    "together: it builds a documented reference set from two tools, scores several models against it at resource level, and reports where the reference "
    "set itself is weak."
)

# honest declaration
T["ai_decl"] = [
    "3.8 Use of Generative AI",
    "Generative AI tools were used in four ways in this work. First, the three LLMs described in Section 3.4.1 are the objects of study. Second, LLMs acted as "
    "judges for matching findings and scoring remediation advice, as described in Section 3.4.3. Third, Claude Code, an AI coding assistant from Anthropic, "
    "was used to write and run the scripts that call the models, match and score their output, and generate the figures and tables. Fourth, the same "
    "assistant was used to help draft and revise parts of the text of this dissertation and to read the sample of judge decisions described in Section "
    "3.4.3. The research questions, the TerraGoat dataset and the static analysis tools come from the author's approved proposal. The author is "
    "responsible for the content of the dissertation and for checking it against the underlying data and sources. This declaration is made in line with the "
    "university's guidance on using AI tools in assessments.",
]

# ---------------- 5.6 generalisation check ----------------
_c, _g, _n = CRUNS
cpv = lambda a, b: pv(CPT[(a, b)]["p_exact"])
T["gen_h"] = "5.6 Generalisation Check on Public Repositories and Registry Modules"
T["gen"] = [
    f"TerraGoat is a public, deliberately vulnerable repository and may be familiar to the models, so its results may not describe ordinary code. To test this, the "
    f"same pipeline was run on the {C_N_FILES}-file second dataset described in Section 3.2, which has {C_N_GH} files from public GitHub repositories and {C_N_REG} from "
    "Terraform Registry modules. Only zero-shot prompting was used, because few-shot prompting made no measurable difference on TerraGoat. The tools reported far "
    f"less on this code. Checkov reported {C_RAW_CK} and Trivy {C_RAW_TV} failed checks across the {C_N_FILES} files, against 215 and 113 on the 14 TerraGoat files, "
    f"and only {C_N_CONS} resource-level findings were reported by both, in {C_CONS_FILES} files. Of those {C_N_CONS}, {C_NET} concern security groups and flow logs, "
    "mostly missing rule descriptions and open egress rules, so recall on this dataset rests on very few distinct kinds of finding. The comparison below is "
    "descriptive.",
    f"Table 5.9 gives the results. The ordering of the models was the same as on TerraGoat. Claude covered {CS[_c]['consensus_covered']} of the {C_N_CONS} reference findings "
    f"(recall {f2(CS[_c]['recall'])}), GPT-5.4 {CS[_g]['consensus_covered']} ({f2(CS[_g]['recall'])}) and Nova Pro {CS[_n]['consensus_covered']} ({f2(CS[_n]['recall'])}). Of the findings that separated Claude "
    f"from GPT-5.4, {CPT[(_c,_g)]['only_a']} were found only by Claude and {CPT[(_c,_g)]['only_b']} only by GPT-5.4 ({cpv(_c,_g)}), and the figures against Nova Pro were "
    f"{CPT[(_c,_n)]['only_a']} and {CPT[(_c,_n)]['only_b']} ({cpv(_c,_n)}). The recall gap between Claude and the other two models is therefore not an artefact of TerraGoat. "
    f"Claude also matched {CCV[_c]['all_tool_rows_covered']} of the {C_N_ALL} findings reported by either tool ({pc(CCV[_c]['of_223'])}), GPT-5.4 {pc(CCV[_g]['of_223'])} and Nova Pro {pc(CCV[_n]['of_223'])}.",
    f"Precision behaved very differently. Strict precision fell to {f2(CS[_c]['precision_strict'])} for Claude, {f2(CS[_g]['precision_strict'])} for GPT-5.4 and {f2(CS[_n]['precision_strict'])} for Nova Pro, "
    f"against 0.46 to 0.50 on TerraGoat, and lenient precision to {f2(CS[_n]['precision_lenient'])} to {f2(CS[_g]['precision_lenient'])}. The cause is the volume of findings. Claude reported "
    f"{CS[_c]['findings']} findings, {C_FILES_PER[_c][0]:.1f} per file, GPT-5.4 {CS[_g]['findings']} ({C_FILES_PER[_g][0]:.1f} per file) and Nova Pro {CS[_n]['findings']} ({C_FILES_PER[_n][0]:.1f} per file), while the tools "
    "found little to report in code that is mostly well configured. Strict and lenient precision measure agreement with the tools, so they fall when a model "
    "reports more than the tools do. The exploratory validity check separates the two readings. Of Claude's "
    f"{CVAL[_c]['unmatched']} unmatched findings the judge labelled {CVAL[_c]['valid']} valid, {CVAL[_c]['debatable']} arguable and {CVAL[_c]['invalid']} invalid. Most were therefore best-practice or context-dependent "
    "points and not clear weaknesses. A plausible reason is that library repositories and registry modules expose security settings as input variables, so a "
    "model that flags a default value cannot know whether a caller will override it, but this was not tested. The adjusted precision, counting matched and valid findings, was "
    f"{f2(CVAL[_c]['adjusted_precision_valid'])} for Claude, {f2(CVAL[_g]['adjusted_precision_valid'])} for GPT-5.4 and {f2(CVAL[_n]['adjusted_precision_valid'])} for Nova Pro. GPT-5.4 had the highest adjusted precision here, which reverses the order seen on TerraGoat: it reported "
    f"fewer findings and only {CVAL[_g]['invalid']} was labelled invalid, whereas {CVAL[_n]['invalid']} of Nova Pro's {CVAL[_n]['unmatched']} unmatched findings were labelled invalid, the most unreliable output of the three.",
    f"Remediation advice could be scored for only {CREM[_c]['scored_findings']}, {CREM[_g]['scored_findings']} and {CREM[_n]['scored_findings']} matched findings. The mean scores were {f2(CREM[_c]['mean_of_judges'])}, {f2(CREM[_g]['mean_of_judges'])} and {f2(CREM[_n]['mean_of_judges'])}, "
    f"the same order as before. The two judges agreed less well on this small set, giving the same score to {pc(CAGREE['exact'])} of {CAGREE['n']} items with a weighted kappa of {CAGREE['kappa']:.2f}, "
    "mostly because the second judge scored GPT-5.4's advice lower than the first. These scores are indicative only.",
    "The check supports three cautious conclusions. The ranking of the models and the size of the recall gap held on a second dataset. Agreement with the tools, "
    "measured as precision, is not stable across datasets, because it depends on how many findings the tools report, so a single precision figure from "
    "TerraGoat should not be quoted as a general property of the models. And on well-configured code the stronger model produced a large volume of mostly arguable "
    "findings, which a team would need to triage. The check has clear limits. The reference set has only "
    f"{C_N_CONS} findings, one file was taken per repository, each file was scanned alone and without the module context in which it would normally be used, and the Trivy "
    "policies that the crosswalk does not cover remain tool-only, which lowers the number of consensus findings. The files are public and may also have been seen by the models.",
]
