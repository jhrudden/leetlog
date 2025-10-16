import argparse

from src.command import CompleteCommand, InitCommand, SampleCommand

CMDS = [InitCommand, SampleCommand, CompleteCommand]


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Plan management CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def parser_builder(name: str, description: str):
        return subparsers.add_parser(name, help=description)

    for c in CMDS:
        c.init_parser(parser_builder)

    args = parser.parse_args()

    args.func(args)


if __name__ == "__main__":
    main()
