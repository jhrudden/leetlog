import random

from src.command.base import Command
from src.config import PLANS_DIR
from src.models import Plan


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
