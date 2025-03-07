from pathlib import Path
from typing import Optional

import yaml
from rich.markdown import Markdown
from rich.panel import Panel

from .cli.utils import autosyntax, autotable, console, remove_yaml_prop
from .validations import get_parameters

PLAYBOOKS_DIR = Path.home() / ".satori/playbooks"


def sync():
    """Clone or pull the playbooks repo"""

    try:
        import git
    except ImportError:
        print(
            "The git package could not be imported.",
            "Please make sure that git is installed in your system.",
        )
        return False

    if PLAYBOOKS_DIR.is_dir():
        repo = git.Repo(PLAYBOOKS_DIR)
        repo.branches["main"].checkout(force=True)
        repo.remote().pull()
    else:
        git.Repo.clone_from("https://github.com/satorici/playbooks.git", PLAYBOOKS_DIR)
    return True


def file_finder() -> list[dict]:
    playbooks = []

    for playbook in PLAYBOOKS_DIR.rglob("*.yml"):
        if ".github" in playbook.parts or playbook.name == ".satori.yml":
            continue

        try:
            parameters = get_parameters(yaml.safe_load(playbook.read_text()))
        except Exception:
            parameters = ()

        try:
            yaml_content = yaml.safe_load(playbook.read_bytes())
            scheme = yaml_content.get("settings", {}).get("scheme", "satori")
            
            playbooks.append({
                "uri": f"{scheme}://" + playbook.relative_to(PLAYBOOKS_DIR).as_posix(),
                "name": get_playbook_name(playbook),
                "parameters": ", ".join(parameters),
                "image": get_playbook_image(playbook),
            })
        except Exception as e:
            print(f"Error processing playbook {playbook}: {e}")
            continue

    return playbooks

def get_playbook_image(filename: Path) -> str:
    """Get playbook image from settings or return empty string if not found"""
    try:
        config = yaml.safe_load(filename.read_text())
        return config["settings"]["image"]
    except Exception:
        return ""


def get_playbook_name(filename: Path) -> str:
    """Get playbook name from settings or return empty string if not found"""
    try:
        config = yaml.safe_load(filename.read_text())
        return config["settings"]["name"]
    except Exception:
        return ""


def display_public_playbooks(
    playbook_id: Optional[str] = None, original: bool = False
) -> None:
    if not sync():
        return

    if not playbook_id:  # satori playbook --public
        playbooks = file_finder()
        playbooks.sort(key=lambda x: x["uri"])
        autotable(playbooks)
    else:  # satori playbook satori://x
        path = PLAYBOOKS_DIR / playbook_id.removeprefix("satori://")

        if path.is_file():
            text = path.read_text()
            if original:
                print(text)
                return
            loaded_yaml = yaml.safe_load(text)
            if description := loaded_yaml.get("settings", {}).get("description"):
                if name := loaded_yaml.get("settings", {}).get("name"):
                    description = f"## {name}\n{description}"
                mk = Markdown(description)
                console.print(Panel(mk))
            yml = remove_yaml_prop(text, "description")
            yml = remove_yaml_prop(yml, "name")
            autosyntax(yml, lexer="YAML")
        else:
            console.print("[red]Playbook not found")