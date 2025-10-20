from collections import defaultdict
from datetime import datetime, timedelta, timezone

from src.command.base import Command
from src.config import PLANS_DIR
from src.models import Plan


class ProgressVisualizer:
    """Simple progress visualization for study plans."""

    def __init__(self, plan: Plan):
        self.plan = plan
        self.completion_by_date = self._group_completions_by_date()

    def _group_completions_by_date(self):
        """Group completed questions by date."""
        by_date = defaultdict(int)
        for question in self.plan.questions:
            if question.completed and question.completed_at:
                date_key = question.completed_at.date().isoformat()
                by_date[date_key] += 1
        return by_date

    def render_last_n_days(self, days: int = 30) -> str:
        """Render a simple bar chart of last N days."""
        if not self.completion_by_date:
            return "No completions yet!"

        today = datetime.now().date()
        lines = []

        for i in range(days - 1, -1, -1):
            date = today - timedelta(days=i)
            date_key = date.isoformat()
            count = self.completion_by_date.get(date_key, 0)

            # Simple bar - left aligned
            b = "█" * count if count > 0 else "·"

            # Show date label for today, and every 7 days
            if i == 0:
                label = "Today"
            elif i % 3 == 0:
                label = date.strftime("%b %d")
            else:
                label = ""

            # Format: date label (left), bar, count (right)
            count_str = f" ({count})" if count > 0 else ""
            lines.append(f"  {label:>8} {b}{count_str}")

        return "\n".join(lines)

    def render_stats(self) -> str:
        """Render full statistics view."""
        total = len(self.plan.questions)
        completed = sum(1 for q in self.plan.questions if q.completed)
        percentage = (completed / total * 100) if total > 0 else 0

        bar_width = 30
        filled = int(bar_width * completed / total) if total > 0 else 0
        b = "█" * filled + "░" * (bar_width - filled)

        current_streak = self._calculate_current_streak()

        days_to_render = min(
            30,
            (datetime.now(timezone.utc).date() - self.plan.started_at.date()).days + 1,
        )

        lines = [
            f"Completion of `{self.plan.name}` stats:",
            f"Progress: [{b}] {completed}/{total} ({percentage:.1f}%)",
            f"🔥 Current streak: {current_streak} days",
            "",
            f"Last {days_to_render} days:",
            self.render_last_n_days(days_to_render),
        ]

        return "\n".join(lines)

    def _calculate_current_streak(self) -> int:
        """Calculate current streak of consecutive days."""
        if not self.completion_by_date:
            return 0

        dates = sorted(
            [datetime.fromisoformat(d).date() for d in self.completion_by_date.keys()]
        )

        today = datetime.now().date()
        current_streak = 0
        check_date = today

        while check_date in dates:
            current_streak += 1
            check_date -= timedelta(days=1)

        return current_streak


class StatsCommand(Command):
    """Get stats on progress of a plan"""

    @classmethod
    def init_parser(cls, parser_builder):
        """Initialize parser for the `stat` command."""
        parser = parser_builder("stat", "Get plan stats")
        parser.add_argument(
            "plan_type",
            type=str,
            help="The LeetCode plan to inspect (e.g., 'top-interview-150').",
        )
        parser.set_defaults(func=lambda args: cls(args)())

    def __call__(self) -> None:
        """Execute the stat command."""
        plan_path = PLANS_DIR / f"{self.args.plan_type}.json"
        plan = Plan.load(plan_path)
        vis = ProgressVisualizer(plan)
        print(vis.render_stats())
