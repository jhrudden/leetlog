import json
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field, computed_field


class Question(BaseModel):
    """Represents a single question in a study plan."""

    name: str
    id: str
    completed: bool = Field(default=False)


class Plan(BaseModel):
    """Represents a study plan containing multiple questions."""

    name: str
    questions: list[Question]

    @computed_field()
    @property
    def unsolved_questions(self) -> list[str]:
        """All unsolved questions in this plan."""
        return [q.id for q in self.questions if not q.completed]

    @classmethod
    def load(cls, path: Path) -> "Plan":
        """
        Load a plan from a file.

        Args:
            path: Path to the plan JSON file

        Returns:
            Plan instance

        Raises:
            ValueError: If the file does not exist
        """
        if not path.exists():
            raise ValueError(f"No file present at: {str(path)}")

        with open(str(path), "r", encoding="utf-8") as f:
            return cls.model_validate(json.load(f))
