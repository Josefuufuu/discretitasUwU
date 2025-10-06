
import sys, pathlib

def pytest_sessionstart(session):
    repo_root = pathlib.Path(__file__).resolve().parents[1]
    src = repo_root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
