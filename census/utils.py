import pathlib

def mkdir_p(path):
    """Create directory `path` if it doesn't exist."""
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
