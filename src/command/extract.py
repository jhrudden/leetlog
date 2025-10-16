import json

from src.command.base import Command
from src.config import PLANS_DIR
from src.models import PlanType
from src.parser import PlanParser


class ExtractPlanCommand(Command):
    """Extract questions from raw plan JSON and save to plans directory."""

    @classmethod
    def init_parser(cls, parser_builder):
        """Initialize parser for extract-plan command."""
        parser = parser_builder("extract-plan", "Extract questions from raw plan JSON")
        parser.add_argument(
            "plan_type",
            type=str,
            help="leetcode plan to extract (e.g., 'top-interview-150', '30-days-of-javascript')",
        )
        parser.set_defaults(func=lambda args: cls(args)())

    def __call__(self) -> None:
        """Execute the extract-plan command."""
        plan_type = PlanType(self.args.plan_type)
        output_path = PLANS_DIR / f"{self.args.plan_type}.json"

        if output_path.exists():
            raise ValueError(
                "Plan already in progress. Please delete if you wish to restart"
            )

        parser = PlanParser(kind=plan_type)
        plan = parser.extract()

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(plan.model_dump(), f, indent=2)

        print(f"Extracted {len(plan.questions)} questions to {output_path}")
