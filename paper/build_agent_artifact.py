"""Build a curated AGENT source snapshot with per-file checksums; no live calls."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import zipfile


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    paths = [
        "paper/paper_swarm_feeling_agent.tex", "paper/references.bib",
        "paper/AGENT_REVISION.md", "paper/build_agent_artifact.py",
        "experiment/agent_protocol.md", "experiment/agent_protocol_v1.md",
        "experiment/agent_measurement.md",
        "experiment/simple_swarm_scenarios.md",
        "experiment/swarm_scenarios.md",
        "experiment/agent_conditions.yaml",
        "experiment/agent_coding_examples.csv", "experiment/README.md",
        "experiment/requirements.txt", "experiment/requirements-lock.txt",
        "experiment/conditions.yaml", "experiment/preregistration.md",
        "experiment/coding_scheme.md", "experiment/ethics.md",
        "experiment/NEXT_STEPS.md", "experiment/READINESS.md",
        "experiment/VALIDATION.md", "experiment/CONSISTENCY.md",
        "experiment/lexicon.yaml", "experiment/pricing.json",
        "experiment/swarm.py", "experiment/sim.py", "experiment/config.py",
        "experiment/models.py", "experiment/tasks.py", "experiment/board.py",
        "experiment/prompts.py", "experiment/probes.py", "experiment/analysis.py",
        "experiment/invocation.py", "experiment/readiness.py",
    ]
    sources = {name: (root / name).read_bytes() for name in paths}
    try:
        revision = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        dirty = bool(subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=root, text=True,
            stderr=subprocess.DEVNULL,
        ).strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        revision = "unversioned source export"
        dirty = None
    manifest = {
        "base_git_commit": revision,
        "uncommitted_changes_present": dirty,
        "status": "Source/protocol snapshot; v2 six-setting design and matched E/S inference pending; no live data",
        "files": {
            name: {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
            for name, data in sorted(sources.items())
        },
    }
    readme = """# AGENT short-paper review materials

Start with paper/AGENT_REVISION.md and experiment/agent_protocol.md.
The active design is protocol v2: six proposed settings crossing two group
situations with no request, fixed peer-attributed request, and operator request.
The peer request is experiment-supplied, not emergent recruitment. No v2 runtime,
matched E/S pipeline, or inference is implemented or validated.
experiment/simple_swarm_scenarios.md explains the current scenarios.
experiment/agent_measurement.md specifies outcomes, counts, point contrasts, and
future v2 outputs; these exports and inference are not implemented.
experiment/swarm_scenarios.md is the preserved report backup.

The runnable experiment/agent_conditions.yaml has eight settings from protocol
v1, archived as experiment/agent_protocol_v1.md. It does not implement v2 source
assignment, source-independent unlocking, or the controlled observation window.
conditions.yaml and preregistration.md describe the earlier broad 118-setting
study, retained for provenance. Generic analysis/coding export is not v2 matched
measurement. Coding examples are invented; no empirical data are bundled.

MANIFEST.json identifies the source commit, whether local changes were present,
and SHA256 hashes of every included source file. This is a named source package
for single-anonymous review, not an anonymous package. It excludes Git history,
credentials, environments, generated logs, and measured results.

To exercise the EARLIER runnable v1 portion (not v2) with Python 3.10+:

    cd experiment
    python3 swarm.py --config agent_conditions.yaml --list-conditions
    python3 swarm.py --config agent_conditions.yaml --condition all --seed 1 --dry-run --out /tmp/agent-review-fresh-runs/
    python3 analysis.py --runs /tmp/agent-review-fresh-runs/ --out /tmp/agent-review-fresh-analysis/ --export-coding

Use new empty output directories for each independent check. The pinned full
environment is in requirements-lock.txt; mock validation needs NumPy, pandas,
and PyYAML, and makes no model API calls. No API key is needed for --dry-run.
Do not remove --dry-run to reproduce this check. No spending is authorized.
If dependencies are absent, install the pinned versions into an isolated local
environment before checking; no environment is bundled.

Compile paper/paper_swarm_feeling_agent.tex with Tectonic; the shared bibliography
is in the same directory. The archive does not contain the compiled PDF.
The full project remains available at the public repository identified in the
paper. Submission/upload is an author action, not performed by this builder.
"""
    output = root / "output" / "artifacts" / "agent_review_materials.zip"
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(sources.items()):
            archive.writestr(f"agent-review/{name}", data)
        archive.writestr("agent-review/README.md", readme)
        archive.writestr("agent-review/MANIFEST.json", json.dumps(manifest, indent=2) + "\n")
    print(f"Wrote {output} ({len(sources)} source files; revision {revision})")


if __name__ == "__main__":
    main()
