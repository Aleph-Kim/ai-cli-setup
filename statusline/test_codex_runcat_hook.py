import runpy
import unittest
from datetime import datetime, timedelta
from pathlib import Path


rate_limit_metrics = runpy.run_path(
    str(Path(__file__).with_name("codex-runcat-hook.py"))
)["rate_limit_metrics"]


class ResetTimeTest(unittest.TestCase):
    def test_reset_times(self):
        today = datetime.now().astimezone().replace(hour=2, minute=10, second=0)
        tomorrow = today + timedelta(days=1)
        metrics = rate_limit_metrics({"rate_limits": {
            "primary": {"window_minutes": 300, "used_percent": 51,
                        "resets_at": today.timestamp()},
            "secondary": {"window_minutes": 10080, "used_percent": 9,
                          "resets_at": tomorrow.timestamp()},
        }})
        self.assertEqual(metrics[0]["formattedValue"], "51% (~02:10)")
        self.assertEqual(metrics[1]["formattedValue"],
                         f"9% (~{tomorrow.month}/{tomorrow.day} 02:10)")
        self.assertEqual(metrics[0]["normalizedValue"], 0.51)

    def test_missing_or_invalid_reset(self):
        for reset in (None, "invalid", 1e100):
            with self.subTest(reset=reset):
                metrics = rate_limit_metrics({"rate_limits": {"primary": {
                    "window_minutes": 300, "used_percent": 51, "resets_at": reset,
                }}})
                self.assertEqual(metrics[0]["formattedValue"], "51%")


if __name__ == "__main__":
    unittest.main()
