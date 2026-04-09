import sys
import yaml
from src.orchestrator import run


def main():
    with open("config.yaml") as f:
        config = yaml.safe_load(f)
    run(config)


if __name__ == "__main__":
    sys.exit(main())
