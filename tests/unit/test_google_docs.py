"""Tests for Google Docs importer skill."""

import importlib.util
import json
import os
from pathlib import Path

from click.testing import CliRunner

# Import the module under test
SCRIPT_DIR = Path(__file__).resolve().parents[2] / "skills" / "google_docs" / "scripts"

spec = importlib.util.spec_from_file_location("google_docs", SCRIPT_DIR / "google_docs.py")
google_docs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(google_docs)


class TestExtractDocId:
    def test_raw_id(self):
        assert google_docs._extract_doc_id("1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms") == (
            "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms"
        )

    def test_docs_url(self):
        url = "https://docs.google.com/document/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms/edit"
        assert google_docs._extract_doc_id(url) == ("1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms")

    def test_sheets_url(self):
        url = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms/edit#gid=0"
        assert google_docs._extract_doc_id(url) == ("1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms")

    def test_docs_url_with_query_params(self):
        url = "https://docs.google.com/document/d/abc123_-def/edit?usp=sharing"
        assert google_docs._extract_doc_id(url) == "abc123_-def"

    def test_short_id(self):
        assert google_docs._extract_doc_id("abc123") == "abc123"


class TestParagraphToMd:
    def test_plain_text(self):
        para = {
            "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
            "elements": [{"textRun": {"content": "Hello world", "textStyle": {}}}],
        }
        assert google_docs._paragraph_to_md(para) == "Hello world"

    def test_heading_1(self):
        para = {
            "paragraphStyle": {"namedStyleType": "HEADING_1"},
            "elements": [{"textRun": {"content": "Title", "textStyle": {}}}],
        }
        assert google_docs._paragraph_to_md(para) == "# Title"

    def test_heading_2(self):
        para = {
            "paragraphStyle": {"namedStyleType": "HEADING_2"},
            "elements": [{"textRun": {"content": "Section", "textStyle": {}}}],
        }
        assert google_docs._paragraph_to_md(para) == "## Section"

    def test_heading_3(self):
        para = {
            "paragraphStyle": {"namedStyleType": "HEADING_3"},
            "elements": [{"textRun": {"content": "Subsection", "textStyle": {}}}],
        }
        assert google_docs._paragraph_to_md(para) == "### Subsection"

    def test_bold_text(self):
        para = {
            "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
            "elements": [{"textRun": {"content": "bold", "textStyle": {"bold": True}}}],
        }
        result = google_docs._paragraph_to_md(para)
        assert "**bold**" in result

    def test_italic_text(self):
        para = {
            "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
            "elements": [{"textRun": {"content": "italic", "textStyle": {"italic": True}}}],
        }
        result = google_docs._paragraph_to_md(para)
        assert "*italic*" in result

    def test_link(self):
        para = {
            "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
            "elements": [
                {
                    "textRun": {
                        "content": "click here",
                        "textStyle": {"link": {"url": "https://example.com"}},
                    }
                }
            ],
        }
        result = google_docs._paragraph_to_md(para)
        assert "[click here](https://example.com)" in result

    def test_empty_paragraph(self):
        para = {
            "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
            "elements": [{"textRun": {"content": "\n", "textStyle": {}}}],
        }
        assert google_docs._paragraph_to_md(para) == ""

    def test_bullet_list(self):
        para = {
            "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
            "bullet": {"nestingLevel": 0},
            "elements": [{"textRun": {"content": "item one", "textStyle": {}}}],
        }
        assert google_docs._paragraph_to_md(para) == "- item one"

    def test_nested_bullet(self):
        para = {
            "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
            "bullet": {"nestingLevel": 2},
            "elements": [{"textRun": {"content": "nested", "textStyle": {}}}],
        }
        assert google_docs._paragraph_to_md(para) == "    - nested"


class TestTableToMd:
    def test_simple_table(self):
        table = {
            "tableRows": [
                {
                    "tableCells": [
                        {
                            "content": [
                                {
                                    "paragraph": {
                                        "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                                        "elements": [
                                            {"textRun": {"content": "A", "textStyle": {}}}
                                        ],
                                    }
                                }
                            ]
                        },
                        {
                            "content": [
                                {
                                    "paragraph": {
                                        "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                                        "elements": [
                                            {"textRun": {"content": "B", "textStyle": {}}}
                                        ],
                                    }
                                }
                            ]
                        },
                    ]
                },
                {
                    "tableCells": [
                        {
                            "content": [
                                {
                                    "paragraph": {
                                        "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                                        "elements": [
                                            {"textRun": {"content": "1", "textStyle": {}}}
                                        ],
                                    }
                                }
                            ]
                        },
                        {
                            "content": [
                                {
                                    "paragraph": {
                                        "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                                        "elements": [
                                            {"textRun": {"content": "2", "textStyle": {}}}
                                        ],
                                    }
                                }
                            ]
                        },
                    ]
                },
            ]
        }
        result = google_docs._table_to_md(table)
        assert "| A | B |" in result
        assert "| --- | --- |" in result
        assert "| 1 | 2 |" in result

    def test_empty_table(self):
        assert google_docs._table_to_md({"tableRows": []}) == ""


class TestStructuralElement:
    def test_paragraph_element(self):
        element = {
            "paragraph": {
                "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                "elements": [{"textRun": {"content": "text", "textStyle": {}}}],
            }
        }
        assert google_docs._structural_element_to_md(element) == "text"

    def test_section_break(self):
        element = {"sectionBreak": {}}
        assert "---" in google_docs._structural_element_to_md(element)

    def test_unknown_element(self):
        assert google_docs._structural_element_to_md({"unknown": {}}) == ""


class TestCheckAuthCommand:
    def test_missing_env_var(self):
        runner = CliRunner()
        env = {k: v for k, v in os.environ.items()}
        env.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
        result = runner.invoke(google_docs.cli, ["check-auth"], env=env)
        assert result.exit_code != 0
        assert "not set" in result.output

    def test_file_not_found(self, tmp_path):
        runner = CliRunner()
        env = {k: v for k, v in os.environ.items()}
        env["GOOGLE_APPLICATION_CREDENTIALS"] = str(tmp_path / "nonexistent.json")
        result = runner.invoke(google_docs.cli, ["check-auth"], env=env)
        assert result.exit_code != 0
        assert "not found" in result.output

    def test_valid_credentials_file(self, tmp_path):
        creds = {
            "type": "service_account",
            "client_email": "test@project.iam.gserviceaccount.com",
            "project_id": "my-project",
        }
        creds_file = tmp_path / "creds.json"
        creds_file.write_text(json.dumps(creds))

        runner = CliRunner()
        env = {k: v for k, v in os.environ.items()}
        env["GOOGLE_APPLICATION_CREDENTIALS"] = str(creds_file)
        result = runner.invoke(google_docs.cli, ["check-auth"], env=env)
        assert result.exit_code == 0
        assert "test@project.iam.gserviceaccount.com" in result.output
        assert "my-project" in result.output

    def test_invalid_json(self, tmp_path):
        creds_file = tmp_path / "bad.json"
        creds_file.write_text("not json")

        runner = CliRunner()
        env = {k: v for k, v in os.environ.items()}
        env["GOOGLE_APPLICATION_CREDENTIALS"] = str(creds_file)
        result = runner.invoke(google_docs.cli, ["check-auth"], env=env)
        assert result.exit_code != 0
        assert "invalid JSON" in result.output


class TestDocCommand:
    def test_doc_help(self):
        runner = CliRunner()
        result = runner.invoke(google_docs.cli, ["doc", "--help"])
        assert result.exit_code == 0
        assert "DOC_ID" in result.output

    def test_sheet_help(self):
        runner = CliRunner()
        result = runner.invoke(google_docs.cli, ["sheet", "--help"])
        assert result.exit_code == 0
        assert "SHEET_ID" in result.output
