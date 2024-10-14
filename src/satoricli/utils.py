from pathlib import Path
import yaml
from argparse import ArgumentParser

CREDENTIALS_FILENAME = ".satori_credentials.yml"

config_arg = ArgumentParser(add_help=False)
config_arg.add_argument(
    "--config",
    type=str,
    help="Directory path for the Satori credentials file",
    metavar="DIR"
)

def get_config_path(args):
    if args.config:
        return Path(args.config) / CREDENTIALS_FILENAME
    return Path.home() / CREDENTIALS_FILENAME

def load_config(args):
    config_path = get_config_path(args)
    config = {}

    if config_path.is_file():
        with config_path.open() as f:
            config.update(yaml.safe_load(f))
    else:
        print(f"Warning: No configuration file found at {config_path}")

    return config

def save_config(config: dict, args):
    config_path = get_config_path(args)
    
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with config_path.open("w") as f:
        yaml.safe_dump(config, f)

    print(f"Configuration saved to {config_path}")
