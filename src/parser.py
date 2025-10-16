import json

import requests
from pydantic import BaseModel, Field

from src.models import Plan, Question

LEETCODE_GRAPHQL_ENDPOINT = "https://leetcode.com/graphql/"

PLAN_INFO_QUERY = """    query studyPlanDetail($slug: String!) {  studyPlanV2Detail(planSlug: $slug) {    slug    name    highlight    staticCoverPicture    colorPalette    threeDimensionUrl    description    premiumOnly    needShowTags    awardDescription    defaultLanguage    award {      name      config {        icon        iconGif        iconGifBackground      }    }    relatedStudyPlans {      cover      highlight      name      slug      premiumOnly    }    planSubGroups {      slug      name      premiumOnly      questionNum      questions {        translatedTitle        titleSlug        title        questionFrontendId        paidOnly        id        difficulty        hasOfficialSolution        topicTags {          slug          name        }        solutionInfo {          solutionSlug          solutionTopicId        }      }    }  }}"""


class PlanParser(BaseModel):
    """Extracts a Plan from raw JSON data."""

    plan_name: str = Field()

    def extract(self) -> Plan:
        """Fetch and parse questions from a LeetCode study plan."""
        plan_slug = self.plan_name.replace("_", "-")

        data = self._fetch_plan(plan_slug)
        full_plan = next(iter(data["data"].values()))

        if not full_plan:
            print(f"❌ Failed to find plan: {plan_slug}")
            raise ValueError(f"Plan '{plan_slug}' not found")

        questions = []
        for sub_group in full_plan.get("planSubGroups", []):
            for q in sub_group.get("questions", []):
                questions.append(Question(name=q.get("title"), id=q.get("id")))

        print(f"✓ Extracted {len(questions)} questions from: {plan_slug}")
        return Plan(name=self.plan_name, questions=questions)

    def _fetch_plan(self, plan_slug: str) -> dict:
        """
        Fetch study plan data from LeetCode GraphQL API.

        Args:
            plan_slug: The slug identifier for the study plan (e.g., "top-interview-150")

        Returns:
            Dictionary containing the plan data

        Raises:
            requests.RequestException: If the HTTP request fails
            ValueError: If the response is invalid or plan not found
        """
        try:
            response = requests.post(
                LEETCODE_GRAPHQL_ENDPOINT,
                json={
                    "operationName": "studyPlanDetail",
                    "query": PLAN_INFO_QUERY,
                    "variables": {"slug": plan_slug},
                },
                timeout=10,
            )
            response.raise_for_status()

        except requests.Timeout as e:
            raise requests.RequestException(
                f"Request timed out while fetching plan: {plan_slug}"
            ) from e
        except requests.RequestException as e:
            raise requests.RequestException(
                f"Failed to fetch plan '{plan_slug}' from LeetCode: {e}"
            ) from e

        # Parse JSON response
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON response from LeetCode API for plan '{plan_slug}': {e}"
            ) from e

        # Check for GraphQL errors
        if "errors" in data:
            error_messages = [
                err.get("message", "Unknown error") for err in data["errors"]
            ]
            raise ValueError(
                f"GraphQL errors for plan '{plan_slug}': {', '.join(error_messages)}"
            )

        # Validate response structure
        if "data" not in data:
            raise ValueError(
                f"Unexpected response structure for plan '{plan_slug}': missing 'data' field"
            )

        return data
