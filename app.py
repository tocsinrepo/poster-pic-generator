"""
Poster Pic Generator -- Streamlit UI wrapping FaceFusion for real (deterministic)
face swapping. Point it at a source photo (real faces) and a target image
(a poster, thumbnail, generated scene, whatever) and it composites the real
face(s) onto the target using FaceFusion's face-swap models -- not an AI
re-draw, so no hallucinated eyes/hands/positions.

Run locally (needs real internet access to download FaceFusion's models on
first run -- this will NOT work inside a network-locked-down sandbox):

    pip install -r requirements.txt
    streamlit run app.py
"""

import subprocess
import sys
import tempfile
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
FACEFUSION_DIR = APP_DIR / "facefusion"
FACEFUSION_REPO_URL = "https://github.com/facefusion/facefusion.git"


def ensure_facefusion_cloned() -> None:
    """Clone FaceFusion next to this app on first run."""
    if FACEFUSION_DIR.exists():
        return
    with st.spinner("First-time setup: cloning FaceFusion..."):
        subprocess.run(
            ["git", "clone", "--depth", "1", FACEFUSION_REPO_URL, str(FACEFUSION_DIR)],
            check=True,
        )


def patch_python310_compat() -> None:
    """
    FaceFusion's facefusion/types.py imports `NotRequired` / `TypeAlias` from
    `typing`, which only exists natively on Python 3.11+. On older Pythons
    (e.g. 3.10) this raises an ImportError before anything can run. This adds
    a safe fallback to `typing_extensions`. No-op if already patched or if
    running on Python 3.11+.
    """
    if sys.version_info >= (3, 11):
        return
    types_file = FACEFUSION_DIR / "facefusion" / "types.py"
    if not types_file.exists():
        return
    content = types_file.read_text()
    old = (
        "from typing import Any, Callable, Dict, List, Literal, "
        "NotRequired, Optional, Tuple, TypeAlias, TypedDict"
    )
    if old not in content:
        return  # already patched, or upstream changed -- leave it alone
    new = (
        "from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, TypedDict\n"
        "try:\n"
        "\tfrom typing import NotRequired, TypeAlias\n"
        "except ImportError:\n"
        "\tfrom typing_extensions import NotRequired, TypeAlias"
    )
    types_file.write_text(content.replace(old, new))


def run_face_swap(source_path: Path, target_path: Path, output_path: Path, face_order: str) -> subprocess.CompletedProcess:
    cmd = [
        sys.executable,
        str(FACEFUSION_DIR / "facefusion.py"),
        "headless-run",
        "-s", str(source_path),
        "-t", str(target_path),
        "-o", str(output_path),
        "--processors", "face_swapper",
        "--face-selector-order", face_order,
    ]
    return subprocess.run(cmd, cwd=str(FACEFUSION_DIR), capture_output=True, text=True)


st.set_page_config(page_title="Poster Pic Generator", page_icon="\U0001F3AD")
st.title("\U0001F3AD Poster Pic Generator")
st.caption(
    "Put real faces from a source photo onto a target image (a poster, thumbnail, "
    "generated scene) using FaceFusion -- a real deterministic face swap, not an "
    "AI re-draw. No hallucinated eyes, hands, or swapped positions."
)

ensure_facefusion_cloned()
patch_python310_compat()

col1, col2 = st.columns(2)
with col1:
    source_file = st.file_uploader("Source photo (real face(s) to use)", type=["jpg", "jpeg", "png"])
    if source_file:
        st.image(source_file, caption="Source", use_container_width=True)
with col2:
    target_file = st.file_uploader("Target image (where the face(s) go)", type=["jpg", "jpeg", "png"])
    if target_file:
        st.image(target_file, caption="Target", use_container_width=True)

face_order = st.selectbox(
    "Order faces appear in the SOURCE photo, left to right (matches them onto the target in the same order)",
    ["left-right", "right-left", "top-bottom", "bottom-top", "small-large", "large-small"],
    index=0,
)

run = st.button("Run Face Swap", type="primary", disabled=not (source_file and target_file))

if run:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        src_path = tmp_path / f"source_{source_file.name}"
        tgt_path = tmp_path / f"target_{target_file.name}"
        out_path = tmp_path / "output.png"
        src_path.write_bytes(source_file.getvalue())
        tgt_path.write_bytes(target_file.getvalue())

        with st.spinner("Running face swap (first run also downloads FaceFusion's models -- can take a few minutes)..."):
            result = run_face_swap(src_path, tgt_path, out_path, face_order)

        if result.returncode == 0 and out_path.exists():
            st.success("Done")
            st.image(str(out_path), caption="Result", use_container_width=True)
            st.download_button(
                "Download result",
                data=out_path.read_bytes(),
                file_name="face_swap_result.png",
                mime="image/png",
            )
        else:
            st.error("FaceFusion did not produce an output. See the log below.")
            st.code((result.stdout or "") + "\n" + (result.stderr or ""))
