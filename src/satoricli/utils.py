from pathlib import Path
import yaml
import argparse

def load_config(config_path=None):
    config = {}

    locations = [
        Path(".satori_credentials.yml"),
        Path.home() / ".satori_credentials.yml",
    ]

    if config_path:
        locations.insert(0, Path(config_path))

    for location in locations:
        if not location.is_file():
            continue

        config.update(yaml.safe_load(location.read_text()))

    return config

def save_config(config: dict):  # TODO: Global/local config
    with (Path.home() / ".satori_credentials.yml").open("w") as f:
        f.write(yaml.safe_dump(config))

def main():
    export_arg = argparse.ArgumentParser(description="Satori CLI")
    export_arg.add_argument("--config", type=str, help="Path to the configuration file")



if __name__ == "__main__":
    main()
