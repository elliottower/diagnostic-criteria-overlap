"""Where the pinned source artifacts live.

They are not in this repository. One copy is shared across every paper that
cites the same work, under the citations library:

    $CITATIONS_HOME/artifacts

`reference/FETCH_LOG.json` pins each one by sha256, so a moved or edited
artifact is detectable from what this repo does track.
"""
from __future__ import annotations

import os
import pathlib


class ArtifactsUnavailable(RuntimeError):
    pass


def artifacts_dir() -> pathlib.Path:
    home = os.environ.get("CITATIONS_HOME")
    if not home:
        raise ArtifactsUnavailable(
            "CITATIONS_HOME is unset. Point it at the citations library:\n"
            "  export CITATIONS_HOME=~/Documents/GitHub/citations-library")
    path = pathlib.Path(home).expanduser() / "artifacts"
    if not path.is_dir():
        raise ArtifactsUnavailable(f"no artifacts directory at {path}")
    return path
