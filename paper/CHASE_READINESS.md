# CHASE extended abstract — checks on 2026-10-16

This is a separate research-proposal manuscript, not a shortened report of live
findings. The full paper and its author information remain unchanged. No paper
has been submitted, no one has been contacted, and no paid model call was made.
The current research sequence is in [NEXT_STEPS.md](../experiment/NEXT_STEPS.md).

## Requirements and remaining author actions

The [CHASE 2027 research-track call](https://conf.researchr.org/track/chase-2027/chase-2027-papers)
permits research proposals as extended abstracts, with five pages total including
references. It specifies IEEE 10-point conference formatting and double-anonymous
review. The recommended abstract-registration deadline is October 16, 2026, AoE;
the paper deadline is October 23, 2026, AoE. Submission is through the official
HotCRP link in the call. This documentation does not register or submit anything.

Before submitting, the authors must:

- Review the entire proposal, retained source claims, authorship, and the disclosure
  of AI assistance. The authors remain responsible for the final work.
- Complete HotCRP author information, conflicts, abstract, and applicable policy
  declarations; keep identifying information out of the review PDF. Retain the
  existing full-paper author order in submission metadata. Do not infer missing
  co-author email addresses or ORCID identifiers.
- Prepare a curated anonymous artifact package and access instructions, or
  finalize the manuscript's explanation that no anonymous package is ready.
  An explanation is currently included; neither package preparation nor a
  reviewer-access test has been completed. Do not link the identifying public
  repository. Check the call's public-title and preprint rules before review.
- Complete screen-reader/reading-order and formal accessibility review. The PDF
  passes the basic checks below but is not a tagged or certified accessible PDF.
  If the venue needs a tagged PDF, use compatible tooling or obtain author-side
  remediation without shrinking fonts or altering IEEE spacing.
- Recheck current instructions and submission fields at the point of submission.
  Live data are not necessary for the proposal category and must not be invented.

## Build and verification

Source: `paper_swarm_feeling_chase.tex`. Bibliography: shared `references.bib`.
From this directory:

```sh
mkdir -p /tmp/swarm-chase-build
tectonic --outdir /tmp/swarm-chase-build --keep-logs paper_swarm_feeling_chase.tex
```

The preview is `../output/pdf/paper_swarm_feeling_chase.pdf`, excluded from Git.
Tectonic 0.17.0 builds the proposal to **three US-letter pages including all
14 references**, within the five-page cap. This is an upper limit, not a target
to fill with extra text. Standard IEEE font sizes and spacing are retained;
repeated prose was shortened rather than changing the template. The reference
list has minor underfull line warnings for long links, with no visible overlap
or clipped content. BibTeX finishes without unresolved entries. The full draft
still cites its original 52 keys; the shared database now has 53 entries because
the proposal adds an official Codex citation for disclosure.

Checks performed:

- Rendered and inspected every proposal page, including the six-comparison table,
  section transitions, disclosure, and references.
- Parsed the PDF with pypdf: selectable/extractable text on every page, expected
  title and table, US-letter dimensions, no unresolved reference markers or red
  empirical placeholders, and no encryption.
- Inspected PDF font descriptors: all used fonts embedded. PDF language is English.
- Checked source, extracted text, link destinations, metadata, and catalog for
  author names, affiliation, email, identifying repository URLs, or local paths.
  No identifying match was found. The remaining producer field identifies only
  the generic PDF compiler, not an author. No author/XMP identity is supplied.
- Checked all 14 cited keys against unique entries and their primary sources as
  described below. Confirmed the full manuscript source matches its pre-task
  version and historical validation reports and experiment code are unchanged.
- Checked the final diff for whitespace errors and that generated PDFs/logs are
  ignored. Harness regressions were not rerun: no runtime behavior changed.

Basic text/font checks do not certify reading order, table semantics, PDF/UA, or
screen-reader usability. No human-perception study, completed human coding,
empirical power estimate, or live-model finding is implied by this build.

## Retained-source checks

The checks below verified bibliographic identity and the specific narrow claim
used in this proposal. Author abstracts and primary institutional/publisher
records were used where full texts were not available. This is not a systematic
novelty search, independent replication, or a fresh audit of all 53 database
entries. Existing entries were preserved. No precise external effect sizes are
reported in this proposal.

| Key | Primary source checked | Claim supported and limit |
|---|---|---|
| peter2025anthropomorphic | [Publisher record and abstract](https://doi.org/10.1073/pnas.2415898122), [author-hosted paper](https://jevinwest.org/papers/Peter2025PNAS.pdf) | Perspective on benefits and risks of human-like conversational agents; not evidence that this study changes developer trust. |
| metr2026hf | [Investigators' report](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) | Communication, scorer-directed coordination, and self-risking experiments; retrospective investigation with stated limits. |
| openai2026hfblog | [Original company account](https://openai.com/index/hugging-face-incident-and-the-road-ahead/) | Reported reward hacking and adoption of others' goals; not independent evidence of subjective states. |
| rajamanoharan2025selfpreservation | [Authors' analysis](https://www.alignmentforum.org/posts/wnzkjSmrgWZaBa2aC/self-preservation-or-instruction-ambiguity-examining-the) | Instruction priority and goal-conflict comparisons; compliance findings are environment-specific. |
| knecht2026shutdown | [Author preprint](https://arxiv.org/html/2609.28274v1) | Group shutdown sabotage and routine framing; sabotage differs from accepting a stopping request. |
| li2025altruism | [Author abstract](https://arxiv.org/abs/2509.22537) | Costly helping and message-board influence in a social dilemma; this proposal does not adopt claims of intrinsic altruistic motives. |
| keeling2024tradeoffs | [Author abstract](https://arxiv.org/abs/2411.02432) | Choices involving points and stipulated pain/pleasure; wording does not establish experienced discomfort. |
| tagliabue2025probing | [Author abstract, revised 2026 version](https://arxiv.org/abs/2509.07961) | Verbal/behavioral preference comparisons in virtual settings; welfare interpretation remains uncertain. |
| hung2026instrument | [Author abstract](https://arxiv.org/abs/2608.23641) | Question-format comparisons holding models and outcomes fixed; motivates separate-format reporting. |
| perez2023selfreports | [Author abstract](https://arxiv.org/abs/2311.08576) | Proposal for making self-reports informative under specified conditions, not validation of current reports. |
| shanahan2023roleplay | [Publisher abstract and metadata](https://www.nature.com/articles/s41586-023-06647-8) | Role play as a framework for interpreting dialogue-agent behavior. Full publisher text is subscription restricted. |
| lakens2017equivalence | [Author's institutional record and abstract](https://research.tue.nl/en/publications/equivalence-tests-a-practical-primer-for-t-tests-correlations-and/) | Nonsignificance does not establish equivalence; formal equivalence testing is not implemented here. |
| long2024welfare | [Author abstract](https://arxiv.org/abs/2411.00986) | Precaution under uncertainty about AI welfare, not a claim that current agents experience distress. |
| openai2026codex | [Official product page](https://openai.com/codex/) | Identifies the tool used for assistance. Access year is not a claimed product-release date or model-version citation. |

The intended empirical predictions remain in the draft study plan. All five new
recommendations are explicitly pending in the roadmap; none was silently added
to the implemented 118-condition configuration by this manuscript conversion.
