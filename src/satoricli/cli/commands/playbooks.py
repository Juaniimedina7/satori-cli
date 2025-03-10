from argparse import ArgumentParser
from typing import Optional
from pathlib import Path
import yaml

from satoricli.api import client
from satoricli.cli.utils import autoformat, autotable

from ..utils import BootstrapTable, console, get_offset
from .base import BaseCommand



class PlaybooksCommand(BaseCommand):
    name = "playbooks"

    def register_args(self, parser: ArgumentParser):
        parser.add_argument(
            "-p",
            "--page",
            dest="page",
            type=int,
            default=1,
            help="Playbooks page number",
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=int,
            default=20,
            help="Page limit number",
        )
        parser.add_argument(
            "--public", action="store_true", help="Fetch public satori playbooks"
        )
        parser.add_argument("--monitor", help="A bool value")

    def __call__(
        self, page: int, limit: int, public: bool, monitor: Optional[str], **kwargs
    ):
        PLAYBOOKS_DIR = Path.home() / ".satori/playbooks"
        offset = get_offset(page, limit)
        params: dict = {"offset": offset, "limit": limit}
        if public:
            data = client.get("/playbooks/public", params=params).json()
            data["rows"] = [row for row in data["rows"] if row["uri"] != "satori://.satori.yml"]
            
            for row in data["rows"]:
                try:
                    playbook_path = PLAYBOOKS_DIR / row["uri"].removeprefix("satori://")
                    if playbook_path.is_file():
                        config = yaml.safe_load(playbook_path.read_text())
                        row["image"] = config.get("settings", {}).get("image", "")
                except Exception:
                    row["image"] = ""
        else:
            if monitor:
                params["monitor"] = monitor
            data = client.get("/playbooks", params=params).json()

        if public and not kwargs["json"]:
            sast_list = filter(lambda x: not bool(x.get("parameters")), data["rows"])
            dast_list = filter(lambda x: bool(x.get("parameters")), data["rows"])
            console.rule("SAST")
            autotable([{
                "uri": x["uri"], 
                "name": x["name"],
                "image": x.get("image", "")
            } for x in sast_list])
            console.rule("DAST")
            autotable([{
                "uri": x["uri"],
                "name": x["name"],
                "parameters": "\n".join(x["parameters"]),
                "image": x.get("image", "")
            } for x in dast_list])
        elif kwargs["json"]:
            autoformat(data["rows"], jsonfmt=kwargs["json"], list_separator="-" * 48)
        else:
            autotable(BootstrapTable(**data), limit=limit, page=page, widths=(16,))
        