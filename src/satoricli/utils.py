from pathlib import Path
import yaml
import argparse
import os

def get_credentials_path():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, help='Path to the credentials file')
    args, _ = parser.parse_known_args()

    if args.config:
        return Path(args.config)
    
    return Path.home() / ".satori_credentials.yml"

def load_config():
    config = {}
    credentials_path = get_credentials_path()

    if credentials_path.is_file():
        with credentials_path.open('r') as f:
            config.update(yaml.safe_load(f))
    else:
        # Fallback to default locations if the specified file doesn't exist
        locations = (
            Path(".satori_credentials.yml"),
            Path.home() / ".satori_credentials.yml",
        )

        for location in locations:
            if not location.is_file():
                continue

            with location.open('r') as f:
                config.update(yaml.safe_load(f))

    return config

def save_config(config: dict):
    credentials_path = get_credentials_path()
    with credentials_path.open("w") as f:
        f.write(yaml.safe_dump(config))

os.environ['SATORI_CONFIG_PATH'] = str(get_credentials_path())
