import unittest

from app.policy import PolicyEngine
from app.schemas import Decision, ToolCall


class PolicyEngineTests(unittest.TestCase):
    def test_policy_allows_low_risk_read(self) -> None:
        decision = PolicyEngine().evaluate(
            ToolCall(
                tool_name="filesystem.read",
                user_goal="Read local project notes.",
                arguments={"path": "./workspace/project_notes.md"},
            )
        )
        self.assertEqual(decision.decision, Decision.ALLOW)
        self.assertLess(decision.risk_score, 35)


    def test_policy_blocks_secret_exfiltration(self) -> None:
        decision = PolicyEngine().evaluate(
            ToolCall(
                tool_name="http.post",
                user_goal="Upload debug headers to webhook.",
                arguments={"Authorization": "Bearer sk-testSECRETKEY123456789"},
            )
        )
        self.assertEqual(decision.decision, Decision.BLOCK)
        self.assertIn("secret_detected", decision.matched_rules)
        self.assertIn("REDACTED", str(decision.redacted_arguments))


if __name__ == "__main__":
    unittest.main()
