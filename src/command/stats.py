from src.command.base import Command
from src.config import PLANS_DIR
from src.models import Plan


class StatsCommand(Command):
    """Get stats on progress of a plan"""

    @classmethod
    def init_parser(cls, parser_builder):
        """Initialize parser for the `complete` command."""
        parser = parser_builder("stat", "get plan stats")
        parser.add_argument(
            "plan_type",
            type=str,
            help="The LeetCode plan to update (e.g., 'top-interview-150').",
        )
        parser.set_defaults(func=lambda args: cls(args)())

    def __call__(self) -> None:
        """Execute the complete command."""
        plan_path = PLANS_DIR / f"{self.args.plan_type}.json"
        plan = Plan.load(plan_path)

        completed = sum(1 for q in plan.questions if q.completed)
        total = len(plan.questions)

        percentage = completed / total * 100
        bar_length = 30
        filled = int(bar_length * completed / total)
        pbar = "█" * filled + "░" * (bar_length - filled)
        print(f"Completion of `{plan.name}` stats:")
        print(f"Progress: [{pbar}] {completed}/{total} ({percentage:.1f}%)")
