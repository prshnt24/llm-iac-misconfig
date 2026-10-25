"""Revisions applied on top of thesis_text.T after the supervisor's comments and the marking report.

Import this module after thesis_text; it edits T in place. Numbers come from thesis_data via thesis_text.
"""
import json as _json
from thesis_text import *  # noqa: F401,F403
from thesis_text import T, v, cz, cf, gz, gf, nz, nf, prec_s
import llm_evaluation as _ev

# cross references: Section 3.4 is now one section
for _k in ("scope", "ai_decl", "models", "matching", "threats", "metrics", "avail"):
    _v = T[_k]
    if isinstance(_v, list):
        T[_k] = [x.replace("Section 3.4.1", "Section 3.4").replace("Section 3.4.3", "Section 3.4") for x in _v]
    else:
        T[_k] = _v.replace("Section 3.4.1", "Section 3.4").replace("Section 3.4.3", "Section 3.4")

# Chapter 1 scope: argue the AWS choice
T["scope"] += (
    " AWS was chosen because it is the setting of the two closest benchmarks, ACSE-Eval (Munshi et al., 2025) and IaC-Eval (Kon et al., 2024), so the results "
    "can be read alongside them, and because both scanners exercise many AWS policies on TerraGoat (95 Checkov and 47 Trivy policies reported failures)."
)

# Section 3.2.2: justify one file per repository
T["gh_note"] += (
    " One file was taken per repository because files from the same repository share authors, conventions and often copied blocks, so they are not independent "
    "observations, and a single large project could otherwise dominate the sample. The cost is that a different file from the same repository could give "
    "different results, so the sample describes a spread of projects and not any one project in depth."
)

# Section 3.4 as one section
T["llm_intro"] = (
    "This section describes how the model output that answers RQ1 to RQ3 was produced and scored. It follows the order in which the data move through stages 4 "
    "to 8 of the pipeline in Figure 3.1: the models and their settings, the prompts, the matching of model findings to the reference set, and the scoring of "
    "remediation advice. Each step exists to turn a free-text answer from a model into counts that can be compared with the reference set built in Section 3.3, "
    "and the final paragraph states how the outputs of this section feed the metrics in Section 3.5."
)
T["models"] = (
    "Three models were evaluated: Claude Sonnet 4.6 (Anthropic), GPT-5.4 (OpenAI) and Amazon Nova Pro (Amazon). All were called through the Amazon Bedrock "
    "Converse interface in the Asia Pacific (Sydney) region, using the inference profiles au.anthropic.claude-sonnet-4-6, global.openai.gpt-5.4 and "
    "apac.amazon.nova-pro-v1:0. The proposal named GPT-4o and Gemini 2.5 Pro. Neither was available through the account the researcher had, and obtaining "
    "separate provider accounts and keys would have delayed the work beyond the submission date. Claude Sonnet 4.6 was retained as proposed. GPT-5.4 replaces "
    "GPT-4o as the OpenAI model. It is a later release, and no claim is made here about how the two compare. Amazon Nova Pro replaces Gemini 2.5 Pro. The two "
    "come from different vendors, and no evidence is offered that one is stronger than the other, so the results cannot be used to infer how Gemini 2.5 Pro would "
    "have performed. The substitution has three consequences for the research questions. First, RQ1 and RQ2 are answered for Claude Sonnet 4.6, GPT-5.4 and "
    "Amazon Nova Pro, and statements about LLMs in general are limited to what three models can show. Second, the ranking found here cannot be extended to "
    "GPT-4o or Gemini 2.5 Pro, and Section 6.4 proposes repeating the study with them. Third, the design is unaffected, because the prompts, matching, scoring "
    "and reference set do not depend on the model, so the same pipeline can be rerun with other models by changing one identifier. Temperature was set to 0 for "
    "Claude Sonnet 4.6 and Nova Pro. GPT-5.4 rejects the temperature parameter on Bedrock, so its default sampling was used, and repeat runs of that model could "
    "differ. The maximum output length was 16,000 tokens for Claude and GPT-5.4 and 9,000 for Nova Pro, whose limit is 10,000. Each model-prompt-file "
    f"combination was run once, giving 84 requests on TerraGoat " + (f"on {FIRST[:10]}." if FIRST[:10] == LAST[:10] else f"between {FIRST[:10]} and {LAST[:10]}.")
)
T["prompts"] = T["prompts"].replace(
    "Two prompt strategies were evaluated. In the zero-shot condition,",
    "Each file was sent to every model under two prompt strategies. In the zero-shot condition,")
T["llm_end"] = (
    "The outputs of this section feed the metrics in Section 3.5. Matched findings give the precision and recall that answer RQ1, the category of each matched "
    "finding gives the category-level results for RQ2, and the remediation scores give RQ3. Because every output is saved with its model, strategy and file, any "
    "figure in Chapter 5 can be traced back to the response and the matching decision that produced it."
)

# Section 3.5: resolve the tension in RQ1
T["metrics"] += (
    " RQ1 is therefore operationalised in two parts. For the models, it is answered by precision, recall and F1-score against the consensus set. For the "
    "comparison with Checkov and Trivy, it is answered by coverage, because accuracy measured against a set that the tools define would be circular. This "
    "refines how RQ1 is measured and leaves its aim unchanged."
)
T["avail"] += " Appendix E reproduces output from the experiment runs, and Appendix F lists the scripts."

# Figure 3.1 explanation
T["fig31_lead"] = (
    "Figure 3.1 below provides a graphical overview of the full evaluation pipeline, from dataset collection through to metric calculation. The text after the "
    "figure explains each of its eight stages and what it is for."
)
T["fig31_caption"] = "Figure 3.1. Evaluation pipeline: from datasets and static analysis, through the reference set, to model runs, matching and scoring."
T["fig31"] = [
    "Stage 1 is the data. The 14 TerraGoat AWS files form the primary benchmark, and 30 GitHub files and 16 Registry module files form the second dataset used to "
    "check whether the TerraGoat results hold elsewhere. Every later stage is applied to each file in the same way. Stage 2 runs Checkov v3.3.9 and Trivy 0.73.0 on "
    "every file. The two tools are independent implementations with separate rule sets, and each reports findings against named resources.",
    "Stage 3 turns the two lists of tool findings into a reference set. The crosswalk in Appendix C links the 41 Trivy policies that have a clear Checkov "
    "equivalent, findings are grouped by file, resource and policy, and a group is a consensus finding when both tools report it. The reference set is needed "
    "because stage 5 has to decide whether a model finding is right, and that requires something to compare it with (Section 3.3). It takes two forms, the "
    "consensus set and the set of all tool findings, which give the strict and lenient scoring used later.",
    "Stage 4 is the experiment itself. Each file is sent to each of three models under two prompts, zero-shot and few-shot, and the answer is saved as a JSON list "
    "of findings with a resource, an issue, a risk and a remediation (Section 3.4). Stage 5 reads each saved answer, without knowing which model produced it, "
    "and maps every finding to the tool findings it describes. The result is a count of hits, misses and unmatched findings for every model and prompt. Stage 6 "
    "turns those counts into precision, recall and F1-score, coverage of the tools' findings, category-level recall and exact tests, which answer RQ1 and RQ2.",
    "Two stages work on the same matched findings. Stage 7 scores the remediation advice of every finding that matched a consensus finding, using two "
    "independent judges and a 0 to 2 rubric, which answers RQ3. Stage 8 is an exploratory check of the findings that matched nothing: a judge reads the "
    "Terraform source and labels each one valid, arguable or invalid. It does not change any score. It shows how much of the shortfall in strict precision reflects "
    "real issues that the tools did not report. The same stages were applied to the second dataset, with zero-shot prompting only.",
]

# Section 2.7: stop restating the research questions
T["rq_ref"] = (
    "This dissertation addresses that gap through the three research questions stated in Section 1.3. They ask how accurately LLMs detect Terraform "
    "misconfigurations compared with Checkov and Trivy, which categories of misconfiguration they handle best and worst, and how closely their remediation advice "
    "matches expert-defined fixes."
)

# Literature: limits of the scanners, and a sharper reading of ACSE-Eval
T["lit_tools"] = (
    "Evidence on how well these tools perform is thinner than their use suggests. A survey of static analysis for IaC catalogues the techniques, defect categories "
    "and target platforms of research tools (Chiari et al., 2022), and the empirical security studies cited in Section 2.2 use scanners as measuring instruments. "
    "Searches carried out for this dissertation found practitioner comparisons of Checkov, tfsec and Terrascan, but no peer-reviewed study that measured their "
    "false-positive rates or how far they agree with each other. Verdet et al. (2025) illustrate the dependence: they assessed adoption of Terraform practices "
    "using Checkov and tfsec, so their figures are only as sound as those scanners' rules. Checkov's policies are mapped to public frameworks such as the CIS "
    "Amazon Web Services Foundations Benchmark (Center for Internet Security, n.d.) and to controls in NIST SP 800-53 (Joint Task Force, 2020). The mapping gives "
    "each rule an external rationale, but it states what a rule is meant to enforce and not how often the rule is right. Chapter 5 supplies one data point on "
    "that question: on the TerraGoat files, the two scanners agree on about a third of what either reports."
)
T["lit_acse"] = (
    "The design of ACSE-Eval also bears on how its results should be read. Its reference threat models were written by experts for each architecture, and model "
    "output is scored with threat framework coverage, ROUGE-L and cosine similarity of embeddings, with each task run three times at temperature 0 (Munshi et al., "
    "2025). Text-overlap scores reward similar wording, and the paper does not describe how an output threat is matched to a reference threat, so it is hard to "
    "tell how much of a score reflects correct security reasoning. The authors themselves note that automated metrics may not capture reasoning quality. The "
    "present study differs on each point: matching is at resource level and its procedure and audit are reported, the reference set comes from tools and not from "
    "expert-written text, and each condition is run once, which is weaker than their three repeats."
)

# Chapter 4 link section
T["ch4_next"] = (
    "This chapter has described what Checkov reports for the TerraGoat AWS module: 221 failed checks across 14 files, concentrated in a few resource types, with "
    "rds.tf alone holding 82. These counts come from one tool, so they show what Checkov flags and not which of those findings are real. Chapter 5 therefore takes "
    "three further steps. It adds the Trivy scan and aligns the two tools through the crosswalk in Appendix C, which gives the consensus findings that serve as "
    "the reference set. It then runs the three models on the same 14 files, matches their findings to that reference set, and scores their detection and "
    "remediation advice. Finally, it repeats the evaluation on a second dataset to see whether the TerraGoat results carry over to other code."
)

# Figure captions with interpretation
T["captions"] = {
    "Figure 4.1:": "Figure 4.1: TerraGoat AWS: Checkov findings by misconfiguration category. Bars give the number of failed checks in each category; Encryption at Rest is the largest, with 37 findings (16.7%).",
    "Figure 4.2:": "Figure 4.2: Distribution of misconfigurations by category (percentage). The chart shows each category's share of the 221 failed checks, so it gives the same ranking as Figure 4.1 in relative terms.",
    "Figure 4.3:": "Figure 4.3: TerraGoat AWS: Checkov findings by configuration file. Bars rank the 14 files by failed checks; rds.tf holds 82 of the 221 (37.1%), far more than any other file.",
    "Figure 4.4:": "Figure 4.4: Heatmap of misconfiguration category against configuration file (Checkov findings). Darker cells mean more findings; the darkest cells are in rds.tf, for Encryption at Rest, Logging and Monitoring, and Other.",
    "Figure 4.5:": "Figure 4.5: Top 20 most triggered Checkov policy IDs in the TerraGoat AWS module. Nine RDS cluster checks tie at nine occurrences each, which reflects the nine near-identical cluster blocks in rds.tf.",
    "Figure 5.1.": "Figure 5.1. Tool findings and candidate consensus. The first two bars are raw finding counts (215 for Checkov, 113 for Trivy); the third is the number of deduplicated resource-level groups on which both tools agree (75). The units differ, so the heights are not directly comparable.",
}
T["cap52"] = ("Figure 5.2. Consensus findings by category. Encryption at rest (20) and network exposure (13) are the largest groups. IAM over-permissioning has none, "
              "because the single IAM finding on which the tools agree was assigned to another category by the name-based rules.")
T["cap53"] = (f"Figure 5.3. Strict precision, recall and F1-score by model and prompt. Strict precision lies between {f2(min(prec_s))} and {f2(max(prec_s))} in every condition, "
              "so the differences in F1-score come from recall, which is highest for Claude Sonnet 4.6.")
T["cap54"] = ("Figure 5.4. Recall by category, model and prompt. Each cell is the share of that category's consensus findings that the model reported; darker cells mean higher "
              "recall. The number of consensus findings in each category is shown in the row label, and categories with one to four findings should be read with caution.")
T["rq1"][0] += (" Figure 5.3 plots the same strict scores: the three bars for each condition are precision, recall and F1-score, and the near-constant height of the "
                "precision bars is the first thing to notice.")
T["rq2"][0] = T["rq2"][0].replace(
    "Table 5.7 and Figure 5.4 show recall by category.",
    "Table 5.7 and Figure 5.4 show recall by category; the figure presents the same numbers as a heat map, in which darker cells mean higher recall and each row "
    "label gives the number of consensus findings in the category.")

# Discussion: extended
_files = sorted((ROOT / "terragoat/terraform/aws").glob("*.tf"))
_in = sum(len(_ev.build_prompt(s, f.read_text(encoding="utf-8"))) for s in ("zeroshot", "fewshot") for f in _files) // 4
_out = sum(len(_json.load(open(f, encoding="utf-8"))["response"]) for r in RUNS[:2] for f in (ROOT / "responses" / r).glob("*.tf.json")) // 4
_cl_cost = (_in * 3.0 + _out * 15.0) / 1e6
_per_req = _cl_cost / 28
T["disc_acse"] = (
    "Compared with ACSE-Eval, where GPT-4.1 and Gemini 2.5 Pro led on threat identification and Claude 3.7 Sonnet was less consistent at categorisation (Munshi et al., "
    "2025), Claude Sonnet 4.6 led here. The studies differ in task, in scoring method, in the generation of Claude model and in the models compared, so the "
    "difference should not be read as a reversal. One possibility is that reviewing a single resource against a known weakness rewards the systematic "
    "enumeration that Claude produced, while threat modelling over a whole architecture rewards other abilities. This is a suggestion and was not tested."
)
T["disc_tools"] = (
    "The agreement figure matters beyond this study. Studies that estimate how common Terraform misconfigurations are, or how widely security practices are adopted, "
    "rely on the output of a scanner (Verdet et al., 2025). If two widely used scanners agree on only about a third of the findings in a benchmark, prevalence "
    "estimates depend heavily on which scanner is used, and an estimate from one scanner is a lower bound on what a reviewer might find. The comparison here covers "
    "one benchmark and a hand-built crosswalk, so the size of the disagreement may differ elsewhere. The direction is still a reason to report which scanner and "
    "which policy set produced any prevalence figure, and ideally to report results from more than one."
)
T["disc_practice"] = (
    "For a DevSecOps team, the results suggest a layered use. Run Checkov and Trivy on every change, since both are cheap and repeatable and each finds things the "
    "other misses, and use the union of their findings and not either alone. Add a model review of the changed files as a second pass, and treat its output as a "
    "list of questions for a reviewer and not as a gate, because on well-configured code the strongest model reported about eight findings per file and most of "
    f"the unmatched ones were arguable. The cost is small: the 28 Claude requests on TerraGoat cost about {_cl_cost:.2f} US dollars at list prices, or about "
    f"{100 * _per_req:.0f} cents per file, although each request here carried one file and a team would need to budget for larger ones. The study did not "
    "integrate a model into a pipeline or measure reviewer time, so these are recommendations drawn from the findings and not tested practice."
)
T["disc_why"] = (
    "The one place where the data allow a test is the short answers for rds.tf. GPT-5.4 and Nova Pro returned one and two findings for that file, and both "
    "responses are complete, valid JSON arrays, so the output was not cut off by the token limit. The models chose to report little for nine near-identical "
    "blocks. Across the whole TerraGoat run, GPT-5.4 reported "
    f"{v(gz,'findings')} findings and Nova Pro {v(nz,'findings')} against {v(cz,'findings')} for Claude in the zero-shot condition, so the pattern is general terseness and not a failure "
    "specific to one file, although it costs most where the same issue repeats many times. Whether a prompt that names every resource would change this was not tested."
)
T["disc_fewshot"] = (
    "Three explanations for the absence of a few-shot effect fit the data, and the study cannot choose between them. Two examples may be too few to shift "
    "models that already review code well. The models may already know the task, so examples add little beyond the instruction. Or the JSON format may constrain "
    f"the answer so strongly that examples add nothing. The one clue is that few-shot prompting changed how much Claude reported ({v(cz,'findings')} findings against {v(cf,'findings')}) without changing "
    "what it matched to the consensus set, which suggests that the examples influenced the volume and style of the answer more than the detection itself. Testing "
    "more examples, examples from other categories, or a prompt without the format constraint would separate these accounts."
)
T["disc_format"] = (
    "The JSON output format raised the concern that it might favour models that follow format instructions closely. The data do not show this: all 84 responses "
    "on TerraGoat parsed as valid JSON arrays, so no model lost findings to formatting, and the differences between models are differences in what they reported."
)
_d = T["disc"]
T["disc"] = [_d[0], T["disc_acse"], _d[1], T["disc_tools"], T["disc_practice"], _d[2], T["disc_why"], T["disc_fewshot"], T["disc_format"]]

# Chapter 6: significance connected to the wider literature
T["c6"]["6.2 Contributions"].append(
    "These contributions connect to the wider literature in three ways. First, the agreement figure is a caution for work that estimates prevalence or "
    "adoption from scanner output (Rahman et al., 2019; Verdet et al., 2025). Such estimates depend on the scanner and rule set used, and this study gives a "
    "measured example of how far two scanners can differ, which the author's searches did not find reported for Checkov and Trivy. Second, for the literature on LLMs in "
    "security review (Pearce et al., 2022; Ullah et al., 2024; Munshi et al., 2025), the study adds a resource-level scoring method that is auditable, and a "
    "result that model choice matters far more than prompt choice for Terraform review, in line with the model dependence those studies report. Third, for "
    "practice, the study supports a layered use of scanners and a model, described in Section 5.7, and shows that the cost of the model step is small compared "
    "with the review effort it adds."
)
