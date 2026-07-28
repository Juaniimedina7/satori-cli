import platform
import shutil
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Literal

import httpx

from satoricli.cli.utils import console, error_console

from .base import BaseCommand


def detect_install_method() -> Literal["pipx", "uv", "pip"]:
    parts = Path(sys.prefix).resolve().parts
    if "pipx" in parts and "venvs" in parts:
        return "pipx"
    if "uv" in parts and "tools" in parts:
        return "uv"
    return "pip"


def build_update_args(method: Literal["pipx", "uv", "pip"]) -> list[str] | None:
    if method == "pipx":
        if not shutil.which("pipx"):
            return None
        return ["pipx", "upgrade", "satori-ci"]

    if method == "uv":
        if not shutil.which("uv"):
            return None
        return ["uv", "tool", "upgrade", "satori-ci"]

    # Pin latest from PyPI to avoid installing from cache
    response = httpx.get("https://pypi.org/pypi/satori-ci/json")
    latest = response.json()["info"]["version"]
    args = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "-U",
        f"satori-ci=={latest}",
    ]
    # Needed on PEP 668 externally-managed system Pythons
    if sys.prefix == getattr(sys, "base_prefix", sys.prefix):
        args.append("--break-system-packages")
    return args


class UpdateCommand(BaseCommand):
    name = "update"

    def register_args(self, parser: ArgumentParser):
        pass

    def __call__(self, **kwargs):
        method = detect_install_method()
        args = build_update_args(method)

        if args is None:
            error_console.print(
                f"Detected {method} install but `{method}` was not found on PATH.",
            )
            return 1

        console.print(f"Going to run: {' '.join(args)}")

        if platform.system() == "Windows":
            subprocess.Popen(args)
            return None

        proc = subprocess.run(args, stdout=sys.stdout, stderr=sys.stderr, check=False)

        return proc.returncode
