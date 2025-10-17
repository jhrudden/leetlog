import json
from datetime import datetime

from src.command.base import Command
from src.config import PLANS_DIR
from src.models import Plan


class CompleteCommand(Command):
    """Mark specified questions in a plan as complete."""

    @classmethod
    def init_parser(cls, parser_builder):
        """Initialize parser for the `complete` command."""
        parser = parser_builder("complete", "Mark questions as complete in a plan")
        parser.add_argument(
            "plan_type",
            type=str,
            help="The LeetCode plan to update (e.g., 'top-interview-150').",
        )
        parser.add_argument(
            "ids",
            nargs="+",
            help="One or more question IDs to mark as complete.",
        )
        parser.set_defaults(func=lambda args: cls(args)())

    def __call__(self) -> None:
        """Execute the complete command."""
        if not self.args.ids:
            raise ValueError("At least one question ID is required.")

        plan_path = PLANS_DIR / f"{self.args.plan_type}.json"
        plan = Plan.load(plan_path)

        ids_to_mark = set(self.args.ids)
        marked = 0

        for q in plan.questions:
            if q.id in ids_to_mark:
                q.completed = True
                q.completed_at = datetime.now()
                marked += 1

        with open(plan_path, "w", encoding="utf-8") as f:
            json.dump(plan.model_dump(mode="json"), f, indent=2)

        print(f"✅ Marked {marked} question(s) as complete in {self.args.plan_type}")
