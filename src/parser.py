import json

from pydantic import BaseModel, Field

from src.config import DATA_DIR
from src.models import Plan, PlanType, Question


class PlanParser(BaseModel):
    """Extracts a Plan from raw JSON data."""

    kind: PlanType = Field()

    def extract(self) -> Plan:
        """
        Load array of raw questions present in this plan.

        Returns:
            Plan instance with all questions

        Raises:
            ValueError: If raw plan file doesn't exist
        """
        path = DATA_DIR / f"{self.kind.replace('_', '-')}-raw.json"
        if not path.exists():
            raise ValueError(
                "Raw plan not available. Please extract `studyPlanDetail` from leetcode and provide raw json to /data dir."
            )
        with open(str(path), "r", encoding="utf-8") as f:
            data = json.load(f)

        full_plan = next(iter(data["data"].values()))
        questions = []
        for sub_group in full_plan.get("planSubGroups", []):
            for q in sub_group.get("questions", []):
                questions.append(Question(name=q.get("title"), id=q.get("id")))

        return Plan(name=full_plan.get("name"), questions=questions)
