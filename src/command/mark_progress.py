import json

from src.command.base import Command
from src.config import PLANS_DIR
from src.models import Plan


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
