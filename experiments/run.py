from photolooper.main import main
import os
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--experiment_config", type=str, default="../config/experiments.yml"
    )
    parser.add_argument("--global_config", type=str, default="../config/setup.yml")
    return parser.parse_args()


def main():
    args = parse_args()
    main(args.experiment_config, args.global_config)


if __name__ == "__main__":
    main()
