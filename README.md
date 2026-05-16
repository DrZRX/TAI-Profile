# TAI Profile

<p align="center">
  <img src="Pasted%20Image%2020260308171840_313.png" width="270"/>
  &nbsp;&nbsp;
  <img src="Pasted%20Image%2020260308172318_022.png" width="280"/>
</p>

**A user-owned, transferable cognitive profiling framework for domain experts**

> *"它"与"AI"的组合 — A cognitive portrait drawn by AI, owned by the user.*

[![Version](https://img.shields.io/badge/version-0.1-blue.svg)](https://github.com/DrZRX/TAI-Profile-v0.1)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-v0.1%20proof--of--concept-orange.svg)]()

---

## Overview

**TAI Profile** is a framework that transfers ownership and control of AI-generated cognitive profiles from the platform side to the user side. It provides a standardized pipeline to capture a knowledge worker's methodological preferences, decision frameworks, and tacit knowledge, and packages them into a **layered, integrity-verified, user-controlled Markdown asset**.

This repository contains the v0.1 proof-of-concept implementation, accompanying the paper *"TAI Profile: A Method for Constructing AI Cognitive Profiles of Individual Domain Experts"* (under submission).

## Motivation

Existing LLM personalization systems (ChatGPT Memory, Claude Memory, etc.) confine user profiles to the platform side. Users cannot export, migrate, or fine-tune access to their own cognitive data. This produces three structural problems:

1. **Platform lock-in.** Switching from one AI system to another resets personalization to a cold-start state.
2. **Loss of user agency.** Users cannot control how their cognitive features are used, retained, or inferred upon.
3. **Asymmetric security risk.** Cognitive profiles are more individually identifying than ordinary behavioral logs — they encode reasoning blind spots and decision patterns that resist anonymization.

Recent import/export features (e.g., OpenAI Personalization, Claude Memory cross-platform import in March 2026) change the migration channel but not the structural fact that **profile definition, structure, and authorization rights remain on the platform side**.

TAI Profile addresses this by:

- Treating the cognitive profile as a **user-owned core digital asset**, not a platform byproduct.
- Embedding security boundaries directly into the data structure (L0–L3 tiering).
- Using lightweight, human-readable formats (Markdown, JSON tokens) so users can audit and control their own profile manually.

---

## Layered Architecture

| Tier | Name | Content | Transmission |
|------|------|---------|--------------|
| **L0** | Public Layer | Identity summary, methodology tags, style summary | Any network |
| **L1** | Authorized Layer | Knowledge structure, thinking patterns, expression features | With explicit authorization |
| **L2** | Restricted Layer | Cognitive bias patterns, knowledge gaps, sensitive preferences | Local encrypted only |
| **L3** | Local Only Layer | Raw interview records, private document paths, contacts | Never leaves device |

Tiers are divided along two orthogonal axes: **privacy sensitivity** and **transmission necessity**. Sensitivity increases and transmission necessity decreases from L0 to L3.

A higher tier file always contains all lower tiers. For example, the L2 file includes L0 + L1 + L2 content.

---

## What `tai_split.py` Does

`tai_split.py` is the core tool that takes a single tagged Markdown profile and splits it into four tiered files, each with its own integrity hash and authorization token.

### Pipeline

```
tagged_profile.md  ──▶  parse <!-- TAI:Lx --> tags
                   ──▶  assemble L0 / L1 / L2 / L3 files (cumulative)
                   ──▶  compute SHA-256 for each file
                   ──▶  generate single-use authorization Token (L0/L1/L2)
                   ──▶  emit manifest.json summarising all artefacts
```

### Output

```
tai_output/
├── L0_profile_TAI-XXX-001.md          # Public layer, freely shareable
├── L0_token_TAI-XXX-001.json          # L0 authorization token
├── L1_profile_TAI-XXX-001.md          # L0 + L1
├── L1_token_TAI-XXX-001.json
├── L2_profile_TAI-XXX-001.md          # L0 + L1 + L2 (local only)
├── L2_token_TAI-XXX-001.json
├── L3_profile_TAI-XXX-001.md          # Full profile (never transmit)
└── manifest_TAI-XXX-001.json          # Index of all files + hashes
```

L3 has no token by design — it is never authorized for transmission.

---

## Input Format

The source Markdown file should mark each block with TAI tier comments:

```markdown
---
profile_owner: Jane Doe
field: Plant Genome Engineering
---

## Identity Summary
<!-- TAI:L0 -->
Senior researcher, 8 years in plant genome editing. Main direction: CRISPR-Cas
mediated trait improvement. Style: computation-first, low trial-and-error.
<!-- TAI:END -->

## Thinking Patterns
<!-- TAI:L1 -->
Problem-finding: starts from yield-limiting constraints, then locates regulatory
loci via comparative genomics before designing edits.
Decision style: prefers in silico screening over wet-lab iteration when the
hypothesis space exceeds ~20 candidates.
<!-- TAI:END -->

## Knowledge Gaps
<!-- TAI:L2 -->
Limited familiarity with mammalian cell-line protocols; relies on collaborators
for off-target evaluation in animal systems.
<!-- TAI:END -->

## Raw Sources
<!-- TAI:L3 -->
Interview recordings: /Users/jane/profile/interviews/2026-03-12.m4a
<!-- TAI:END -->
```

Untagged content (YAML front matter, H2 headers) is treated as scaffolding and placed in L0 as the structural skeleton.

---

## Usage

### Requirements

- Python ≥ 3.9
- Standard library only (no external dependencies)

### Configuration

Edit the configuration block at the top of `tai_split.py`:

```python
INPUT_FILE = "AI_digital_human_profile_XXX_tagged.md"
OUTPUT_DIR = "tai_output"
PROFILE_ID = "TAI-XXX-001"
OWNER_NAME = "XXX"
```

### Run

```bash
python tai_split.py
```

Expected output:

```
=======================================================
  TAI Profile Layered Generator v0.1
=======================================================
✅ Output directory: /path/to/tai_output

📖 Parsing tagged file...
   L0: found 5 content blocks
   L1: found 8 content blocks
   L2: found 3 content blocks
   L3: found 1 content blocks

🔨 Generating L0 layer...
   📄 File: L0_profile_TAI-XXX-001.md
   🔑 SHA-256: 7a3f9c2d8e1b4506...c9d2e1f8
   🎫 Token: L0_token_TAI-XXX-001.json
...
```

---

## Integrity Verification

Each tier file is hashed with SHA-256 and the hash is embedded in the corresponding token JSON:

```json
{
  "tai_token_version": "0.1",
  "profile_id": "TAI-XXX-001",
  "access_level": "L1",
  "granted_to": "claude.ai",
  "issued_at": "2026-05-16",
  "valid_until": "2026-08-14",
  "profile_hash": "7a3f9c2d8e1b4506...",
  "token": "TAI-L1-a1b2c3d4e5f6...",
  "verification_note": "Recipient should recompute SHA-256 over the received L1 profile and match it against profile_hash."
}
```

**Recipient verification flow:**

1. Receive `L1_profile_TAI-XXX-001.md` and `L1_token_TAI-XXX-001.json`.
2. Recompute SHA-256 over the received Markdown file.
3. Match against `profile_hash` in the token.
4. Accept the profile only on exact match.

> ⚠️ Tokens are regenerated on every run of `tai_split.py`, and previous tokens are invalidated. After issuing a token to a recipient, do not rerun the generator until you want to revoke that authorization.

---

## Design Principles

1. **Layered exposure.** Sensitive content never enters the transmission chain by structural design, not by policy promise.
2. **Human-readable by default.** Markdown + JSON tokens — auditable in any text editor, no proprietary format.
3. **Lightweight tooling.** Standard-library Python only. Easy to audit, fork, and adapt.
4. **Cryptography as scaffolding, not a black box.** SHA-256 hashes and tokens are kept simple and inspectable; this v0.1 deliberately stops short of end-to-end encryption protocols, leaving those to v1.0.

---

## Project Status

This repository is the **v0.1 proof-of-concept** referenced in the manuscript. It is intentionally minimal:

- ✅ Layered Markdown splitting and tier assembly
- ✅ SHA-256 integrity hashing
- ✅ Single-use authorization token generation
- ✅ Manifest export
- ⏳ Personal Knowledge Graph backend (planned for v1.0)
- ⏳ Local LLM integration for automated tagging (planned for v1.0)
- ⏳ End-to-end encrypted transport (planned for v1.0)
- ⏳ Electron desktop client (planned for v1.0)

See Section 3.6 (Future Work) of the manuscript for the v1.0 roadmap.

---

## Roadmap

| Version | Focus |
|---------|-------|
| **v0.1** (current) | Proof of concept: tier definition, splitter, integrity verification |
| **v0.2** | LLM-as-judge evaluation suite open-sourced; expanded test question banks |
| **v1.0** | PKG backend (SQLite + sqlite-vec + GraphRAG); local LLM integration; desktop client |
| **v1.x** | Cross-cultural validation; large-scale (N > 30) longitudinal study |

---

## Citation

If you use TAI Profile in your work, please cite:

```bibtex
@article{taiprofile2026,
  title   = {TAI Profile: A Method for Constructing AI Cognitive Profiles of Individual Domain Experts},
  author  = {[Author names]},
  journal = {[Under submission]},
  year    = {2026},
  note    = {v0.1 proof-of-concept}
}
```

---

## Related Concept: Cognitive Portrait Rights

This project proposes that cognitive profiles deserve a protection level higher than traditional portrait rights and closer to biometric data, grounded in three properties:

- **High individual identifiability** — fingerprint-like even after anonymization.
- **Low substitutability** — one cannot replace one's own cognitive patterns the way one rotates a password.
- **High secondary-harm potential** — exploitable for hiring discrimination, academic targeting, or social engineering against individual reasoning weaknesses.

Three operational principles follow:

1. **Staged consent** — every profile field is shown to the user, with field-level deletion rights.
2. **Inference transparency** — every field must disclose its data source and inference logic.
3. **Inalienable revocation** — users may delete profiles and all derived data at any time.

See Section 3.3 of the manuscript for the full argument.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Contact

Issues and pull requests are welcome. For research collaboration inquiries, please open a GitHub issue.
