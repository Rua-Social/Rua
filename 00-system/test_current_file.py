"""The loaded client-job instructions keep one current deliverable."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
SHOOT = (ROOT / "00-system/skills/rua-shoot-plan/SKILL.md").read_text(encoding="utf-8")
TREATMENT = (ROOT / "00-system/skills/rua-treatment/SKILL.md").read_text(encoding="utf-8")
STORAGE = (ROOT / "20-studio/storage.md").read_text(encoding="utf-8")
CONTRACT = (ROOT / "00-system/rewrite-contract.md").read_text(encoding="utf-8")
REISSUE = (
    ROOT / "00-system/skills/rua-shoot-plan/references/reissue-protocol.md"
).read_text(encoding="utf-8")


def section(text: str, heading: str, stop: str) -> str:
    start = text.index(heading)
    end = text.index(stop, start + len(heading))
    return text[start:end]


class CurrentFileRuleTests(unittest.TestCase):
    def test_agents_states_the_four_outcomes(self) -> None:
        rule = section(AGENTS, "## Current file", "## Founder and business intent")
        self.assertIn("instance record has a file index", rule)
        self.assertIn("that index names the current file", rule)
        self.assertIn("Offload is scratch", rule)
        self.assertIn("not current when the index names a different file", rule)
        self.assertIn("working location that index already names", rule)
        self.assertIn("Rewrite the file index so it names the new version", rule)
        self.assertIn("Keep the previous current file", rule)
        self.assertIn("off the current list", rule)
        self.assertIn("Move that previous set out of the working location", rule)
        self.assertIn("place for earlier versions", rule)
        self.assertIn("earlier-versions folder outside the working location", rule)
        self.assertIn("holds only the files the index lists as current", rule)
        self.assertIn("more than one form of the same deliverable", rule)
        self.assertIn("update those forms together", rule)
        self.assertIn("capture-only note", rule)
        self.assertIn("`rua vault current REF`", rule)
        self.assertIn("pass is not finished", rule)

    def test_deck_and_treatment_follow_the_same_rule(self) -> None:
        self.assertNotIn("latest dated file is canonical", SHOOT)
        versioning = " ".join(section(SHOOT, "**Versioning.**", "**Change log.**").split())
        self.assertIn("Current file in `AGENTS.md`", versioning)
        self.assertIn("one the instance file index names", versioning)
        self.assertIn("working location that index already names", versioning)
        self.assertIn("rewrites the index", versioning)
        self.assertIn("keeps the previous file", versioning)
        self.assertIn("no longer listed as current", versioning)
        self.assertIn("Move it out of the working location", versioning)
        self.assertIn("earlier-versions folder outside the working location", versioning)
        self.assertIn("move together", versioning)
        self.assertIn("does not create a new offload folder", versioning)
        self.assertIn("`rua vault current REF`", versioning)
        self.assertIn("pass is not finished", versioning)
        self.assertIn("`rua vault current REF`", TREATMENT)
        self.assertIn("pass is not finished", TREATMENT)
        self.assertIn("Current file in `AGENTS.md`", TREATMENT)
        self.assertIn("every form the index lists", TREATMENT)
        self.assertIn("off the current list", TREATMENT)
        self.assertIn("move it out of the working location", TREATMENT)
        self.assertIn("updates every listed form in the same pass", TREATMENT)
        self.assertIn("Follow Current file in `AGENTS.md`", CONTRACT)
        self.assertNotIn("file becomes canonical", REISSUE)
        self.assertIn("because the index names it", REISSUE)
        self.assertIn("keep the previous file", REISSUE)
        self.assertIn("Move it out of the working location", REISSUE)

    def test_storage_note_does_not_move_a_recorded_working_location(self) -> None:
        self.assertIn("working location the instance record names", STORAGE)
        self.assertIn("does not move it", STORAGE)


if __name__ == "__main__":
    unittest.main()
