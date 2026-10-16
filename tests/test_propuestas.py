"""Guards for the proposal form, the interview skill and the reminder.

Non-ASCII needles are written as escapes so failure output stays
cp1252-safe on Windows consoles.
"""

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
FORM = ROOT / ".github" / "ISSUE_TEMPLATE" / "proyecto-nuevo.yml"
CONFIG = ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml"
SKILL = ROOT / "skills" / "proponer-proyecto" / "SKILL.md"
REMINDER = ROOT / ".github" / "workflows" / "recordatorio-propuestas.yml"
FORM_ID = re.compile(r"^    id: (\S+)$", re.M)
LINK = re.compile(r'(?:\]\(|src="|href=")([^)"#\s]+)')


def test_form_disclaimers_and_confirmations():
    text = FORM.read_text(encoding="utf-8")
    assert 'labels: ["propuesta"]' in text
    for needle in [
        "no implica aceptación, compromiso ni respaldo",
        "does not imply acceptance, commitment or endorsement",
        "Este issue es público",
        "This issue is public",
    ]:
        assert needle in text, ascii(needle)
    assert text.count("          required: true") == 4


def test_blank_issues_disabled():
    assert "blank_issues_enabled: false" in CONFIG.read_text(encoding="utf-8")


def test_skill_covers_every_form_field():
    ids = FORM_ID.findall(FORM.read_text(encoding="utf-8"))
    assert ids, "no field ids found"
    skill = SKILL.read_text(encoding="utf-8")
    assert skill.startswith("---\nname: proponer-proyecto\n")
    for field in ids:
        if field == "confirmaciones":
            continue  # the person ticks these; the skill must not prefill them
        assert f"`{field}`" in skill, field


def test_links_point_to_this_repo():
    for p in [FORM, SKILL, ROOT / "README.md"]:
        assert "CFA-Society-Mexico/.github/issues/new" not in p.read_text(encoding="utf-8"), p.name
    for p in [SKILL, ROOT / "README.md"]:
        text = p.read_text(encoding="utf-8")
        assert "propuestas/issues/new?template=proyecto-nuevo.yml" in text, p.name


def test_relative_links_resolve():
    for p in ROOT.rglob("*.md"):
        for target in LINK.findall(p.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            assert (p.parent / target).exists(), f"{p.relative_to(ROOT)} -> {target}"


def test_reminder_never_closes():
    text = REMINDER.read_text(encoding="utf-8")
    assert "only-labels: propuesta" in text
    assert "days-before-close: -1" in text
    assert "days-before-pr-stale: -1" in text
