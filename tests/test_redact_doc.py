# -*- coding: utf-8 -*-
"""Tests for scripts/redact_doc.py.

Every fixture here is invented. The NDIS, Medicare, CRN and phone numbers are
deliberately fake, and the names belong to nobody. Do not replace them with
real family details: this file is public and permanent.

Run with:
    python -m unittest tests/test_redact_doc.py -v
"""
import contextlib
import io
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import redact_doc  # noqa: E402


# A fabricated NDIS plan covering every identifier the tool claims to catch.
FAKE_PLAN = """\
NDIS PLAN REVIEW - PARTICIPANT SUMMARY

Participant: Sarah Whitmore
Date of birth: 14 March 2009
NDIS Number: 430 123 456
Medicare: 2123 45678 1
CRN: 987 654 321 A
Address: 14 Wattle Grove, Reservoir, VIC 3073
Phone: 0412 345 678
Email: sarah.whitmore@example.com
School: Reservoir High School

Review date: 12/03/2027
For help call the NDIS on 1800 800 110.
"""

# A fabricated school plan excerpt.
FAKE_IEP = """\
EDUCATION AND SUPPORT PLAN (EXCERPT)

Student: Amelia Whitmore    Year: 7    DOB: 03/09/2011
School: Reservoir High School
Parent: Mr Daniel Whitmore, 0400 111 222
Home: 14 Wattle Grove, Reservoir VIC 3073
Contact: d.whitmore@example.com

Goals
1. Amelia will request a break using her card before escalation.
2. Staff will offer a quiet space within two minutes of the first sign.

Review: 20 November 2026
"""

NAMES = "Sarah Whitmore, Reservoir High School"


class RedactorTests(unittest.TestCase):
    def setUp(self):
        self.r = redact_doc.Redactor(NAMES.split(", "))

    # ---- individual identifiers ------------------------------------------

    def test_ndis_number_after_keyword(self):
        out = self.r.run("NDIS Number: 430 123 456")
        self.assertIn("[NDIS_NUMBER]", out)
        self.assertNotIn("430", out)

    def test_ndis_number_bare_nine_digits(self):
        out = redact_doc.Redactor([]).run("Reference 123456789 filed.")
        self.assertIn("[NDIS_NUMBER]", out)
        self.assertNotIn("123456789", out)

    def test_medicare_number(self):
        out = redact_doc.Redactor([]).run("Medicare 2123 45678 1 on file.")
        self.assertIn("[MEDICARE_NUMBER]", out)
        self.assertNotIn("45678", out)

    def test_crn(self):
        out = redact_doc.Redactor([]).run("CRN: 987 654 321 A")
        self.assertIn("[CRN]", out)
        self.assertNotIn("987", out)

    def test_email(self):
        out = redact_doc.Redactor([]).run("Write to sarah.whitmore@example.com today.")
        self.assertIn("[EMAIL]", out)
        self.assertNotIn("example.com", out)

    def test_australian_mobile(self):
        for raw in ["0412 345 678", "0412345678", "+61 412 345 678"]:
            with self.subTest(raw=raw):
                out = redact_doc.Redactor([]).run("Call %s please." % raw)
                self.assertIn("[PHONE]", out)
                self.assertNotIn("345 678", out)

    def test_australian_landline(self):
        out = redact_doc.Redactor([]).run("Ring (03) 9123 4567.")
        self.assertIn("[PHONE]", out)

    def test_service_numbers_are_not_redacted(self):
        """1300, 1800 and 13 numbers are not personal, and one is the NDIS line."""
        text = "Call 1800 800 110 or 1300 555 777 or 13 22 00."
        out = redact_doc.Redactor([]).run(text)
        self.assertIn("1800 800 110", out)
        self.assertIn("1300 555 777", out)
        self.assertIn("13 22 00", out)

    def test_street_address(self):
        out = redact_doc.Redactor([]).run("Lives at 14 Wattle Grove, Reservoir.")
        self.assertIn("[ADDRESS]", out)
        self.assertNotIn("Wattle", out)

    def test_state_and_postcode(self):
        out = redact_doc.Redactor([]).run("Reservoir, VIC 3073")
        self.assertIn("[ADDRESS]", out)
        self.assertNotIn("3073", out)

    def test_dob_is_redacted(self):
        for raw in ["DOB: 14 March 2009", "date of birth 03/09/2011", "born 2009-03-14"]:
            with self.subTest(raw=raw):
                out = redact_doc.Redactor([]).run(raw)
                self.assertIn("[DOB]", out)

    def test_ordinary_dates_survive(self):
        """Review dates are the substance of a plan. They must not be scrubbed."""
        text = "Review date: 12/03/2027. Next review 20 November 2026."
        out = redact_doc.Redactor([]).run(text)
        self.assertIn("12/03/2027", out)
        self.assertIn("20 November 2026", out)
        self.assertNotIn("[DOB]", out)

    # ---- names -----------------------------------------------------------

    def test_full_name_and_bare_first_name(self):
        out = self.r.run("Sarah Whitmore rang. Sarah was tired.")
        self.assertIn("[CHILD_A]", out)
        self.assertNotIn("Sarah", out)
        self.assertNotIn("Whitmore", out)

    def test_school_gets_its_own_series(self):
        out = self.r.run("Attends Reservoir High School.")
        self.assertIn("[SCHOOL_A]", out)
        self.assertNotIn("Reservoir High", out)

    def test_school_does_not_swallow_the_suburb(self):
        """A bare-token rule on a school name would turn the suburb into [SCHOOL_A]."""
        out = self.r.run("14 Wattle Grove, Reservoir, VIC 3073")
        self.assertNotIn("[SCHOOL_A]", out)

    def test_adult_titled_name_is_not_a_child(self):
        r = redact_doc.Redactor(["Dr Daniel Whitmore"])
        out = r.run("Seen by Dr Daniel Whitmore.")
        self.assertIn("[PERSON_A]", out)

    def test_pseudonyms_are_consistent(self):
        r = redact_doc.Redactor(["Amelia Whitmore", "Sarah Whitmore"])
        out = r.run("Amelia met Sarah. Amelia left. Sarah stayed.")
        self.assertEqual(out.count("[CHILD_A]"), 2)
        self.assertEqual(out.count("[CHILD_B]"), 2)
        self.assertNotIn("Amelia", out)
        self.assertNotIn("Sarah", out)

    def test_shared_surname_gets_its_own_label(self):
        """A surname shared by two people belongs to neither of them.

        Attributing it to whichever name was processed first would quietly
        assert that a bare "Whitmore" always means the same person.
        """
        r = redact_doc.Redactor(["Amelia Whitmore", "Sarah Whitmore"])
        out = r.run("Whitmore called again.")
        self.assertNotIn("Whitmore", out)
        self.assertIn("[SURNAME_A]", out)

    def test_parent_with_a_title_is_not_labelled_a_child(self):
        """The family types a bare name; the letter says "Mr Daniel Whitmore"."""
        r = redact_doc.Redactor(["Amelia Whitmore", "Daniel Whitmore"])
        out = r.run("Parent: Mr Daniel Whitmore. Student: Amelia Whitmore.")
        self.assertIn("[PERSON_A]", out)
        self.assertIn("[CHILD_A]", out)
        self.assertNotIn("Daniel", out)

    def test_email_is_not_chewed_by_name_substitution(self):
        """Names run last, so an email becomes [EMAIL] and not [CHILD_A].[CHILD_A]@."""
        out = self.r.run("Email sarah.whitmore@example.com")
        self.assertIn("[EMAIL]", out)
        self.assertNotIn("[CHILD_A].", out)

    # ---- whole documents -------------------------------------------------

    def test_fake_plan_leaves_no_identifiers(self):
        out = self.r.run(FAKE_PLAN)
        for secret in ["Sarah", "Whitmore", "430 123 456", "2123 45678",
                       "987 654 321", "Wattle", "3073", "0412 345 678",
                       "sarah.whitmore@example.com", "14 March 2009"]:
            with self.subTest(secret=secret):
                self.assertNotIn(secret, out)

    def test_fake_plan_keeps_its_substance(self):
        out = self.r.run(FAKE_PLAN)
        self.assertIn("NDIS PLAN REVIEW", out)
        self.assertIn("12/03/2027", out)

    def test_fake_iep_leaves_no_identifiers(self):
        r = redact_doc.Redactor(["Amelia Whitmore", "Daniel Whitmore",
                                 "Reservoir High School"])
        out = r.run(FAKE_IEP)
        for secret in ["Amelia", "Whitmore", "03/09/2011", "0400 111 222",
                       "d.whitmore@example.com", "3073"]:
            with self.subTest(secret=secret):
                self.assertNotIn(secret, out)
        # The goals are the useful part and must survive.
        self.assertIn("request a break", out)
        self.assertIn("20 November 2026", out)

    # ---- output discipline ----------------------------------------------

    def test_summary_never_prints_identifiers(self):
        """The terminal scrollback gets screenshotted. Counts only."""
        with tempfile.TemporaryDirectory() as tmp:
            src = pathlib.Path(tmp) / "Sarah-Whitmore-NDIS-plan.txt"
            src.write_text(FAKE_PLAN, encoding="utf-8")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                redact_doc.main([str(src), "--names", NAMES])
            printed = buf.getvalue()
        for secret in ["Sarah", "Whitmore", "430 123 456", "0412 345 678",
                       "sarah.whitmore@example.com"]:
            with self.subTest(secret=secret):
                self.assertNotIn(secret, printed)
        self.assertIn("NDIS_NUMBER", printed)

    def test_output_filename_does_not_leak_a_name(self):
        r = redact_doc.Redactor(NAMES.split(", "))
        stem = r.redact_filename("Sarah-Whitmore-NDIS-plan")
        self.assertNotIn("Sarah", stem)
        self.assertNotIn("Whitmore", stem)
        self.assertTrue(stem.endswith("NDIS-plan"))

    def test_writes_redacted_markdown_beside_the_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = pathlib.Path(tmp) / "plan.txt"
            src.write_text(FAKE_PLAN, encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                rc = redact_doc.main([str(src), "--names", NAMES])
            self.assertEqual(rc, 0)
            dest = src.parent / (redact_doc.Redactor(NAMES.split(", "))
                                 .redact_filename("plan") + ".redacted.md")
            self.assertTrue(dest.exists())
            body = dest.read_text(encoding="utf-8")
            self.assertIn("[NDIS_NUMBER]", body)
            self.assertNotIn("430 123 456", body)

    def test_outdir_is_honoured(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as out:
            src = pathlib.Path(tmp) / "plan.txt"
            src.write_text(FAKE_PLAN, encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                redact_doc.main([str(src), "--names", NAMES, "--outdir", out])
            self.assertEqual(len(list(pathlib.Path(out).glob("*.redacted.md"))), 1)

    def test_html_is_reduced_to_text(self):
        raw = "<html><body><p>NDIS Number: 430 123 456</p></body></html>"
        out = redact_doc.Redactor([]).run(redact_doc.html_to_text(raw))
        self.assertNotIn("<p>", out)
        self.assertNotIn("430 123 456", out)

    def test_unsupported_extension_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = pathlib.Path(tmp) / "plan.docx"
            bad.write_text("x", encoding="utf-8")
            with self.assertRaises(SystemExit):
                redact_doc.read_document(bad)

    def test_missing_file_returns_two(self):
        with contextlib.redirect_stdout(io.StringIO()):
            rc = redact_doc.main(["no-such-file.txt"])
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
