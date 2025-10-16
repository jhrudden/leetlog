import json

from src.command.base import Command
from src.config import PLANS_DIR
from src.models import PlanType
from src.parser import PlanParser


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

        parser = PlanParser(kind=plan_type)
        plan = parser.extract()

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(plan.model_dump(), f, indent=2)

        print(f"Extracted {len(plan.questions)} questions to {output_path}")
