from pathlib import Path
import yaml
import argparse
import os
import sys

CREDENTIALS_FILENAME = ".satori_credentials.yml"

def get_credentials_path():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--config', type=str, help='Directory path for the credentials file')
    
    _, args = parser.parse_known_args(sys.argv[2:])

    config_path = None
    for i, arg in enumerate(args):
        if arg == '--config' and i + 1 < len(args):
            config_path = args[i + 1]
            break
        elif arg.startswith('--config='):
            config_path = arg.split('=', 1)[1]
            break

    if config_path:
        return Path(config_path) / CREDENTIALS_FILENAME
    
    return Path.home() / CREDENTIALS_FILENAME

def load_config():
    config = {}
    credentials_path = get_credentials_path()

    if credentials_path.is_file():
        with credentials_path.open('r') as f:
            config.update(yaml.safe_load(f))
    else:
        default_location = Path.home() / CREDENTIALS_FILENAME
        if default_location.is_file():
            with default_location.open('r') as f:
                config.update(yaml.safe_load(f))

    return config

def save_config(config: dict):
    credentials_path = get_credentials_path()
    credentials_path.parent.mkdir(parents=True, exist_ok=True)
    with credentials_path.open("w") as f:
        f.write(yaml.safe_dump(config))

os.environ['SATORI_CONFIG_PATH'] = str(get_credentials_path())
