import re
import subprocess
from pathlib import Path
import platform

DOIT_CONFIG = {
    "default_tasks": ["format", "lint", "test"],
    "backend": "json",
}

HERE = Path(__file__).parent


def task_format():
    """Reformat all files using black."""
    return {"actions": [["black", HERE], ["isort", HERE]], "verbosity": 1}


def task_format_check():
    """Check, but not change, formatting using black."""
    return {"actions": [["black", HERE, "--check"], ["isort", HERE, "--check-only"]], "verbosity": 1}


def task_test():
    """Run Pytest with coverage."""
    return {
        "actions": ["pytest --cov=biopsykit %(paras)s"],
        "params": [{"name": "paras", "short": "p", "long": "paras", "default": ""}],
        "verbosity": 2,
    }


def task_lint():
    """Lint all files with Prospector."""
    return {"actions": [["prospector"]], "verbosity": 1}


def task_type_check():
    """Type check with mypy."""
    return {"actions": [["mypy", "-p", "biopsykit"]], "verbosity": 1}


def task_docs():
    """Build the html docs using Sphinx."""
    if platform.system() == "Windows":
        return {"actions": [[HERE / "docs/make.bat", "html"]], "verbosity": 2}
    else:
        return {"actions": [["make", "-C", HERE / "docs", "html"]], "verbosity": 2}


def task_register_ipykernel():
    """Add a jupyter kernel with the biopsykit env to your local install."""

    return {
        "actions": [
            ["python", "-m", "ipykernel", "install", "--user", "--name", "biopsykit", "--display-name", "biopsykit"]
        ]
    }


def update_version_strings(file_path, new_version):
    # taken from:
    # https://stackoverflow.com/questions/57108712/replace-updated-version-strings-in-files-via-python
    version_regex = re.compile(r"(^_*?version_*?\s*=\s*\")(\d+\.\d+\.\d+-?\S*)\"", re.M)
    with open(file_path, "r+") as f:
        content = f.read()
        f.seek(0)
        f.write(
            re.sub(
                version_regex,
                lambda match: '{}{}"'.format(match.group(1), new_version),
                content,
            )
        )
        f.truncate()


def update_version(version):
    subprocess.run(["poetry", "version", version], shell=False, check=True)
    new_version = (
        subprocess.run(["poetry", "version"], shell=False, check=True, capture_output=True)
        .stdout.decode()
        .strip()
        .split(" ", 1)[1]
    )
    update_version_strings(HERE / "src/biopsykit/__init__.py", new_version)


def task_update_version():
    """Bump the version in pyproject.toml and biopsykit.__init__ ."""
    return {
        "actions": [(update_version,)],
        "params": [{"name": "version", "short": "v", "default": None}],
    }
