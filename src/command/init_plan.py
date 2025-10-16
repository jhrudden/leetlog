import json

from src.command.base import Command
from src.config import PLANS_DIR
from src.models import PlanType
from src.parser import PlanParser


class InitPlanCommand(Command):
    """Initialize a new LeetCode plan for tracking and progress."""

    @classmethod
    def init_parser(cls, parser_builder):
        """Initialize parser for the `init` command."""
        parser = parser_builder(
            "init",
            "Initialize a LeetCode plan for tracking progress",
        )
        parser.add_argument(
            "plan_type",
            type=str,
            help=(
                "The LeetCode plan to initialize "
                "(e.g., 'top-interview-150', '30-days-of-javascript'). "
                "This will extract its questions and create a local plan file."
            ),
        )
        parser.set_defaults(func=lambda args: cls(args)())

    def __call__(self) -> None:
        """Execute the init command."""
        plan_type = PlanType(self.args.plan_type)
        output_path = PLANS_DIR / f"{self.args.plan_type}.json"

        if output_path.exists():
            raise ValueError(
                "A plan already exists. Delete it first if you want to reinitialize."
            )

        parser = PlanParser(kind=plan_type)
        plan = parser.extract()

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(plan.model_dump(), f, indent=2)

        print(
            f"Initialized {len(plan.questions)} questions for {plan_type.value} at {output_path}"
        )
