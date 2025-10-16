#!/usr/bin/env python3
import argparse
import json
import random
from abc import ABC, abstractmethod
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field, computed_field

DATA_DIR = Path("data")

PLANS_DIR = Path("plans")
PLANS_DIR.mkdir(exist_ok=True)


class Question(BaseModel):
    """Represents a single question in a study plan."""

    name: str
    id: str
    completed: bool = Field(default=False)


class Plan(BaseModel):
    """Represents a study plan containing multiple questions."""

    name: str
    questions: list[Question]

    @computed_field()
    @property
    def unsolved_questions(self) -> list[str]:
        """All unsolved questions in this plan."""
        return [q.id for q in self.questions if not q.completed]

    @classmethod
    def load(cls, path: Path) -> "Plan":
        """
        Load a plan from a file.

        Args:
            path: Path to the plan JSON file

        Returns:
            Plan instance

        Raises:
            ValueError: If the file does not exist
        """
        if not path.exists():
            raise ValueError(f"No file present at: {str(path)}")

        with open(str(path), "r", encoding="utf-8") as f:
            return cls.model_validate(json.load(f))


class PlanType(StrEnum):
    """Enumeration of available plan types."""

    TOP_150 = "top_150"

    def create_plan(self) -> "PlanParser":
        """
        Create a PlanParser from a PlanType.

        Returns:
            PlanParser instance for this plan type
        """
        return PlanParser(kind=self)


class PlanParser(BaseModel):
    """Extracts a Plan from raw JSON data."""

    kind: PlanType = Field()

    def extract(self) -> Plan:
        """
        Load array of raw questions present in this plan.

        Returns:
            Plan instance with all questions

        Raises:
            ValueError: If raw plan file doesn't exist
        """
        path = DATA_DIR / f"{self.kind.replace('_', '-')}-raw.json"
        if not path.exists():
            raise ValueError(
                "Raw plan not available. Please extract `studyPlanDetail` from leetcode and provide raw json to /data dir."
            )
        with open(str(path), "r", encoding="utf-8") as f:
            data = json.load(f)

        full_plan = next(iter(data["data"].values()))
        questions = []
        for sub_group in full_plan.get("planSubGroups", []):
            for q in sub_group.get("questions", []):
                questions.append(Question(name=q.get("title"), id=q.get("id")))

        return Plan(name=full_plan.get("name"), questions=questions)


class Command(ABC):
    """Base class for all CLI commands."""

    def __init__(self, args: argparse.Namespace):
        """
        Initialize command with parsed arguments.

        Args:
            args: Parsed command-line arguments
        """
        self.args = args

    @abstractmethod
    def __call__(self) -> None:
        """
        Execute the command.

        TODO: Implement in subclasses.
        """
        raise NotImplementedError("Subclasses must implement __call__")


class ExtractPlanCommand(Command):
    """Extract questions from raw plan JSON and save to plans directory."""

    def __call__(self) -> None:
        """Execute the extract-plan command."""
        plan_type = PlanType(self.args.plan_type)
        output_path = PLANS_DIR / f"{self.args.plan_type}.json"

        if output_path.exists():
            raise ValueError(
                "Plan already in progress. Please delete if you wish to restart"
            )

        plan_parser = plan_type.create_plan()
        plan = plan_parser.extract()

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(plan.model_dump(), f, indent=2)

        print(f"Extracted {len(plan.questions)} questions to {output_path}")


class SamplePlanCommand(Command):
    """Sample n random question IDs from a plan."""

    def __call__(self) -> None:
        """
        Execute the sample-plan command.

        Returns:
            List of sampled question IDs
        """
        plan_path = PLANS_DIR / f"{self.args.plan_type}.json"
        plan = Plan.load(plan_path)

        question_ids = plan.unsolved_questions

        # Sample n random IDs
        n = min(self.args.n, len(question_ids))
        sampled = random.sample(question_ids, n)

        print(f"Sampled {n} question IDs:")
        for qid in sampled:
            print(f"{qid}")


class MarkCompleteCommand(Command):
    """Mark specified questions as complete."""

    def __call__(self) -> None:
        """Execute the mark-complete command."""
        plan_path = PLANS_DIR / f"{self.args.plan_type}.json"
        plan = Plan.load(plan_path)

        ids_to_mark = set(self.args.ids)

        marked = 0
        for q in plan.questions:
            if q.id in ids_to_mark:
                q.completed = True
                marked += 1

        # Save updated plan
        with open(plan_path, "w", encoding="utf-8") as f:
            json.dump(plan.model_dump(), f, indent=2)

        print(f"Marked {marked} question(s) as complete")


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
