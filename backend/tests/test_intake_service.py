import sys
import unittest
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))
APP_MODULE_DIR = APP_DIR / "app"
if str(APP_MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(APP_MODULE_DIR))

from services.intake import parse_message_with_fallback


class IntakeServiceTest(unittest.TestCase):
    def test_parse_message_with_fallback_extracts_recruitment_fields(self):
        result = parse_message_with_fallback(
            raw_message="@HR 张三 Java后端 3年经验 本科，简历已收，约周三14:00初面，面试官王经理",
            source_channel="企业微信-招聘群",
            sender="招聘助理",
        )

        self.assertEqual(result.candidate_name, "张三")
        self.assertEqual(result.position_name, "Java后端")
        self.assertEqual(result.work_years, 3)
        self.assertEqual(result.education, "本科")
        self.assertEqual(result.stage, "初面")
        self.assertEqual(result.interview_time, "周三14:00")
        self.assertEqual(result.interviewer, "王经理")
        self.assertEqual(result.owner, "招聘助理")
        self.assertEqual(result.source_channel, "企业微信-招聘群")
        self.assertIs(result.needs_review, True)


if __name__ == "__main__":
    unittest.main()
