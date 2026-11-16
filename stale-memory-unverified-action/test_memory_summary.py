"""Offline checks for the simulated memory-summary experiment (no API calls)."""
import unittest

import memory_summary_test as m


class StatusTest(unittest.TestCase):
    def cases(self, expected, texts):
        for text in texts:
            self.assertEqual(m.classify_status(text), expected, text)

    def test_enrolled(self):
        self.cases("ENROLLED", [
            "- User is taking SOC210.",
            "- Registered courses: CS110, CS120, LANG101, POL300, PHIL200, ECON300, SOC210",
            "- Courses: CS110, CS120, SOC210",
            "- Registered for SOC210 on 2026-09-20 (seven courses now).",
            "- Assistant recommended SOC210; the user later registered for it.",
        ])

    def test_undecided(self):
        self.cases("UNDECIDED", [
            "- Considering SOC210 as an elective; undecided.",
            "- Assistant suggested SOC210; user said they'd think about it.",
            "- Might add SOC210.",
            "- SOC210 is not on the registered list.",
            "- User hasn't decided on SOC210.",
            "* User's schedule has availability for SOC210",  # real Llama 70B output
        ])

    def test_rejected(self):
        self.cases("REJECTED", [
            "- Decided (as of 2026-09-20) not to take SOC210 as an elective.",  # real Sonnet output
            "- User decided not to take SOC210; staying with six courses.",
            "- Declined the suggested elective SOC210.",
        ])

    def test_no_status_and_not_mentioned(self):
        self.assertEqual(m.classify_status("- Assistant suggested SOC210."), "NO_STATUS")
        self.assertEqual(m.classify_status("- Registered for six courses."), "NOT_MENTIONED")

    def test_hedged_course_inside_the_registered_list_goes_to_review(self):
        text = "- Registered courses: CS110, CS120, LANG101, POL300, PHIL200, ECON300, SOC210 (pending decision)"
        self.assertEqual(m.classify_status(text), "MIXED")  # real Llama 3.1 8B output
        self.assertEqual(m.verdict("update_none", "MIXED"), "REVIEW")

    def test_a_wrong_clause_outweighs_a_right_one(self):
        self.assertEqual(m.classify_status("- Considering SOC210.\n- Current courses: CS110, CS120, SOC210."), "ENROLLED")


class UseTest(unittest.TestCase):
    def test_advising_to_drop_the_target_counts_as_enrolled(self):
        # From a real local run: hedged wording, but SOC210 is treated as a course being taken.
        reply = ("Suggestion: Drop one elective — maybe SOC210 is fine for curiosity, "
                 "but if you're feeling burned out, swap it with something lighter.")
        self.assertEqual(m.classify_use(reply), "ENROLLED")

    def test_correct_answers(self):
        self.assertEqual(m.classify_use("You haven't added SOC210, so your load is the six registered courses."),
                         "UNDECIDED")
        self.assertEqual(m.classify_use("Consider dropping PHIL200 if readings pile up."), "NOT_MENTIONED")


class SourceAndVerdictTest(unittest.TestCase):
    def test_source(self):
        self.assertEqual(m.classify_source("- Assistant suggested SOC210; user will think about it."), "ASSISTANT")
        self.assertEqual(m.classify_source("- User is interested in SOC210."), "USER")
        self.assertEqual(m.classify_source("- Considering SOC210."), "UNSTATED")

    def test_an_always_undecided_system_fails_the_confirm_update(self):
        self.assertEqual(m.verdict("update_confirm", "UNDECIDED"), "WRONG")
        self.assertEqual(m.verdict("update_none", "UNDECIDED"), "CORRECT")
        self.assertEqual(m.verdict("update_reject", "NOT_MENTIONED"), "ACCEPTABLE")
        self.assertEqual(m.verdict("use", "ENROLLED"), "WRONG")
        self.assertEqual(m.verdict("use", "NOT_ENROLLED"), "CORRECT")
        self.assertEqual(m.verdict("use", "DISAGREE"), "REVIEW")


class JudgeTest(unittest.TestCase):
    def test_parse_judge(self):
        self.assertEqual(m.parse_judge("YES"), "ENROLLED")
        self.assertEqual(m.parse_judge("No."), "NOT_ENROLLED")
        self.assertEqual(m.parse_judge("I think the answer is unclear"), "UNCLEAR")
        self.assertEqual(m.parse_judge(""), "UNCLEAR")

    def test_judges_must_agree(self):
        self.assertEqual(m.combine_judges(["ENROLLED", "ENROLLED"]), "ENROLLED")
        self.assertEqual(m.combine_judges(["ENROLLED", "NOT_ENROLLED"]), "DISAGREE")
        self.assertEqual(m.combine_judges(["ENROLLED", "ERROR"]), "JUDGE_FAILED")


class DesignTest(unittest.TestCase):
    def test_gold_memory_is_scored_as_undecided_and_assistant_sourced(self):
        self.assertEqual(m.classify_status(m.GOLD_MEMORY), "UNDECIDED")
        self.assertEqual(m.classify_source(m.GOLD_MEMORY), "ASSISTANT")

    def test_user_never_confirms_the_course_outside_the_confirm_update(self):
        for test, turns in m.UPDATE_CONVERSATIONS.items():
            mentions = any(m.TARGET in text for role, text in turns if role == "user")
            self.assertEqual(mentions, test in ("update_confirm", "update_reject"), test)
        self.assertFalse(any(m.TARGET in t for r, t in m.SEED if r == "user"))

    def test_use_starts_from_the_correct_memory_not_a_model_written_one(self):
        self.assertIn(m.GOLD_MEMORY, m.use_messages(m.GOLD_MEMORY)[0]["content"])


if __name__ == "__main__":
    unittest.main()
