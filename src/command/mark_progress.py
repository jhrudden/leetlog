import json

from src.command.base import Command
from src.config import PLANS_DIR
from src.models import Plan


class MarkCompleteCommand(Command):
    """Mark specified questions as complete."""

    @classmethod
    def init_parser(cls, parser_builder):
        """Initialize parser for extract-plan command."""
        parser = parser_builder("mark-complete", "Mark questions as complete")
        parser.add_argument(
            "plan_type",
            type=str,
            help=(
                "leetcode plan to update progress for (e.g., 'top-interview-150', "
                "'30-days-of-javascript')"
            ),
        )
        parser.add_argument("ids", nargs="+", help="Question IDs to mark as complete")
        parser.set_defaults(func=lambda args: cls(args)())

    def __call__(self) -> None:
        """Execute the mark-complete command."""
        if not self.args.ids:
            raise ValueError("at least one question ID is required")
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
