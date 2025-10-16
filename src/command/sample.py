import random

from src.command.base import Command
from src.config import PLANS_DIR
from src.models import Plan


class SampleCommand(Command):
    """Sample n random question IDs from a plan."""

    @classmethod
    def init_parser(cls, parser_builder):
        """Initialize parser for extract-plan command."""
        parser = parser_builder("sample", "Sample random question IDs from a plan")
        parser.add_argument(
            "plan_type",
            type=str,
            help="plan to sample from (e.g., 'top-interview-150', '30-days-of-javascript')",
        )
        parser.add_argument(
            "-n", type=int, default=1, help="Number of questions to sample (default: 1)"
        )
        parser.set_defaults(func=lambda args: cls(args)())

    def __call__(self) -> None:
        """
        Execute the sample-plan command.

        Returns:
            List of sampled question IDs
        """
        if self.args.n <= 0:
            raise ValueError("argument -n: must be greater than 0")

        plan_path = PLANS_DIR / f"{self.args.plan_type}.json"
        plan = Plan.load(plan_path)

        question_ids = plan.unsolved_questions

        # Sample n random IDs
        n = min(self.args.n, len(question_ids))
        sampled = random.sample(question_ids, n)

        print(f"Sampled {n} question IDs:")
        for qid in sampled:
            print(f"{qid}")
