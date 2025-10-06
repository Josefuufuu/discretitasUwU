import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parents[1]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

_src_root = _repo_root / "src"
if str(_src_root) not in sys.path:
    sys.path.insert(0, str(_src_root))
