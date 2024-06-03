from photolooper.main import main
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--experiment_config", type=str, default="../config/experiment.yml"
    )
    parser.add_argument("--global_config", type=str, default="../config/setup.yml")
    return parser.parse_args()


def run():
    args = parse_args()
    main(args.global_config, args.experiment_config)


if __name__ == "__main__":
    run()
