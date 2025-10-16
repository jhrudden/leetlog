import argparse

from src.command import ExtractPlanCommand, MarkCompleteCommand, SamplePlanCommand
from src.models import PlanType


def add_plan_type_arg(parser: argparse.ArgumentParser) -> None:
    """
    Add plan_type argument to a parser.

    Args:
        parser: ArgumentParser to add the argument to
    """
    parser.add_argument(
        "plan_type",
        choices=[pt.value for pt in PlanType],
        help="Type of plan to extract",
    )


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Plan management CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # extract-plan command
    extract_parser = subparsers.add_parser(
        "extract-plan", help="Extract questions from raw plan JSON"
    )
    add_plan_type_arg(extract_parser)
    extract_parser.set_defaults(func=lambda args: ExtractPlanCommand(args)())

    # sample-plan command
    sample_parser = subparsers.add_parser(
        "sample-plan", help="Sample random question IDs from a plan"
    )
    add_plan_type_arg(sample_parser)
    sample_parser.add_argument(
        "-n", type=int, default=1, help="Number of questions to sample (default: 1)"
    )
    sample_parser.set_defaults(func=lambda args: SamplePlanCommand(args)())

    # mark-complete command
    complete_parser = subparsers.add_parser(
        "mark-complete", help="Mark questions as complete"
    )
    add_plan_type_arg(complete_parser)
    complete_parser.add_argument(
        "ids", nargs="+", help="Question IDs to mark as complete"
    )
    complete_parser.set_defaults(func=lambda args: MarkCompleteCommand(args)())

    # Parse and validate
    args = parser.parse_args()

    # Validation
    if args.command == "sample-plan" and args.n <= 0:
        parser.error("argument -n: must be greater than 0")

    if args.command == "mark-complete" and not args.ids:
        parser.error("at least one question ID required")

    # Execute command
    args.func(args)


if __name__ == "__main__":
    main()
