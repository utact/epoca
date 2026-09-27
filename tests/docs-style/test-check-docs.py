import importlib.util
import os
import shutil
import stat
import subprocess
import sys
import unittest
import uuid
from contextlib import contextmanager
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "check-docs.py"
SPEC = importlib.util.spec_from_file_location("check_docs", SCRIPT)
CHECKER = importlib.util.module_from_spec(SPEC)
sys.dont_write_bytecode = True
SPEC.loader.exec_module(CHECKER)


def table(value, *, header="수용 기준"):
    return f"| {header} | 확인 방법 |\n| --- | --- |\n| {value} | 동시 요청 테스트 |\n"


@contextmanager
def temporary_workspace():
    parent = Path(__file__).resolve().parent
    folder = parent / f"tmp-{uuid.uuid4().hex}"
    # Inherit parent permissions so restricted Windows accounts can access the directory.
    folder.mkdir()
    try:
        yield folder
    finally:
        if folder.resolve().parent != parent:
            raise RuntimeError("Temporary workspace escaped its test directory")
        def remove_readonly(function, path, error):
            if not isinstance(error, PermissionError):
                raise error
            # Git object files can be read-only on Windows.
            os.chmod(path, stat.S_IWRITE)
            function(path)

        shutil.rmtree(folder, onexc=remove_readonly)


class DocsStyleTests(unittest.TestCase):
    def test_diagnostic_codes(self):
        codes = list(CHECKER.MESSAGES)
        for code in codes:
            with self.subTest(code=code):
                self.assertRegex(code, r"\ADOC(?!000)[0-9]{3}\Z")
        self.assertEqual(sorted(codes), codes)
        spec_text = (SCRIPT.parents[1] / "specs" / "docs-style" / "spec.md").read_text(encoding="utf-8")
        registered = [line.split("|")[1].strip() for line in spec_text.splitlines()
                      if line.startswith("| DOC")]
        self.assertEqual(registered, codes)

    def test_presence_pairs(self):
        for original, corrected in (
            ("색상이 있음", "색상 존재"),
            ("색상이 없음", "색상 부재"),
        ):
            with self.subTest(original=original, corrected=corrected):
                self.assertEqual([(3, 1, "DOC002")], CHECKER.check_text(table(original)))
                self.assertEqual([], CHECKER.check_text(table(corrected)))

    def test_original_failures_and_corrections(self):
        # Observed corrections are recorded in docs/workflow.md under '문체와 마커'.
        for original, corrected in (
            ("동시 추첨과 확정에서 같은 색의 소유자가 중복되지 않음", "동시 추첨·확정 시 색상 소유권의 유일성"),
            ("여러 탭과 연타로 정해진 추첨 횟수를 초과하지 않음", "여러 탭·연타 시 추첨 횟수 상한 준수"),
            ("만료·재방출된 색을 이전 선택 상태로 확정할 수 없음", "만료·재방출 후 이전 선택 상태에 의한 색상 확정 차단"),
            ("유사색·어두운 색·밝은 색에서도 닉네임과 본문을 읽을 수 있음", "유사색·어두운 색·밝은 색에서 닉네임과 본문의 가독성 확보"),
        ):
            with self.subTest(original=original, corrected=corrected):
                self.assertEqual([(3, 1, "DOC002")], CHECKER.check_text(table(original)))
                self.assertEqual([], CHECKER.check_text(table(corrected)))

    def test_predicate_tense_and_form_coverage(self):
        cases = {
            "되다": (
                "색상 선택이 됨",
                "색상 선택이 된다",
                "색상 선택이 됩니다",
                "색상 선택이 되었음/색상 선택이 됐음",
                "색상 선택이 되었다/색상 선택이 됐다",
                "색상 선택이 되었습니다/색상 선택이 됐습니다",
            ),
            "않다": (
                "색상을 변경하지 않음",
                "색상을 변경하지 않는다",
                "색상을 변경하지 않습니다",
                "색상을 변경하지 않았음",
                "색상을 변경하지 않았다",
                "색상을 변경하지 않았습니다",
            ),
            "없다": (
                "선택한 색상이 없음",
                "선택한 색상이 없다",
                "선택한 색상이 없습니다",
                "선택한 색상이 없었음",
                "선택한 색상이 없었다",
                "선택한 색상이 없었습니다",
            ),
            "이다": (
                # These first two forms stand alone to satisfy the word-boundary requirement.
                "임",
                "이다",
                "선택한 색상입니다",
                "선택한 색상이었음/선택한 후보였음",
                "선택한 색상이었다/선택한 후보였다",
                "선택한 색상이었습니다/선택한 후보였습니다",
            ),
            "있다": (
                "선택한 색상이 있음",
                "선택한 색상이 있다",
                "선택한 색상이 있습니다",
                "선택한 색상이 있었음",
                "선택한 색상이 있었다",
                "선택한 색상이 있었습니다",
            ),
            "하다": (
                "색상 선택을 함",
                "색상 선택을 한다",
                "색상 선택을 합니다",
                "색상 선택을 하였음/색상 선택을 했음",
                "색상 선택을 하였다/색상 선택을 했다",
                "색상 선택을 하였습니다/색상 선택을 했습니다",
            ),
        }
        for predicate, forms in cases.items():
            for form_index, variants in enumerate(forms):
                for value in variants.split("/"):
                    with self.subTest(predicate=predicate, form_index=form_index, value=value):
                        self.assertEqual([(3, 1, "DOC002")], CHECKER.check_text(table(value)))

    def test_short_form_boundaries(self):
        for original, expected in (
            ("완료됨", []), ("완료가 됨", [(3, 1, "DOC002")]),
            ("후보임", []), ("임", [(3, 1, "DOC002")]),
            ("후보이다", []), ("이다", [(3, 1, "DOC002")]),
            ("허용함", []), ("허용을 함", [(3, 1, "DOC002")]),
        ):
            with self.subTest(original=original):
                self.assertEqual(expected, CHECKER.check_text(table(original)))

    def test_valid_nouns(self):
        for suffix, values in (
            ("다", ("바다", "사이다")),
            ("음", ("모음",)),
            ("임", ("모임", "책임")),
            ("함", ("결함", "포함")),
        ):
            for value in values:
                with self.subTest(suffix=suffix, value=value):
                    self.assertEqual([], CHECKER.check_text(table(value)))

    def test_punctuation_and_sentence(self):
        # Cross noun/statement with punctuation absent/present to check both diagnostics independently.
        for value, expected in (
            ("색상 존재", []),
            ("색상 존재.", [(3, 1, "DOC001")]),
            ("색상이 있다", [(3, 1, "DOC002")]),
            ("색상이 있다.", [(3, 1, "DOC001"), (3, 1, "DOC002")]),
        ):
            with self.subTest(value=value):
                self.assertEqual(expected, CHECKER.check_text(table(value)))

    def test_header(self):
        for header, expected in (
            ("색상 존재", []),
            ("색상이 있음", [(1, 1, "DOC002")]),
        ):
            with self.subTest(header=header):
                self.assertEqual(expected, CHECKER.check_text(table("색상 존재", header=header)))

    def test_inline_code(self):
        for value, expected in (
            ("색상이 있음", [(3, 1, "DOC002")]),
            ("`색상이 있음`", []),
            ("색상이 없음", [(3, 1, "DOC002")]),
            ("`색상이 없음`", []),
        ):
            with self.subTest(value=value):
                self.assertEqual(expected, CHECKER.check_text(table(value)))

    def test_code_literals(self):
        for kind, value in (
            ("marker", "마커 `1.`"),
            ("nested-backtick", "``print(`색상이 있음`)``"),
            ("path", "`docs/example.md`"),
        ):
            with self.subTest(kind=kind, value=value):
                self.assertEqual([], CHECKER.check_text(table(value)))

    def test_fences(self):
        for marker in ("```", "~~~"):
            with self.subTest(marker=marker):
                self.assertEqual([], CHECKER.check_text(f"{marker}markdown\n{table('색상이 있음')}{marker}\n"))

    def test_pipe_variants_and_line_numbers(self):
        source = "# 문서\n\n기준 | 방법\n:--- | ---:\n색상 \\| 상태 | 테스트\n색상이 있음 | 테스트\n"
        self.assertEqual([(6, 1, "DOC002")], CHECKER.check_text(source))

    def test_links_and_emphasis(self):
        for label, expected in (
            ("색상 존재", []),
            ("색상이 있음", [(3, 1, "DOC002")]),
        ):
            with self.subTest(label=label):
                self.assertEqual(expected, CHECKER.check_text(table(f"[**{label}**](example.md)")))

    def test_non_table_prose(self):
        self.assertEqual([], CHECKER.check_text("색상이 있다.\n\n색상 | 색상이 있음\n표가 아닌 설명이다."))

    def test_cli_exit_codes_and_location(self):
        with temporary_workspace() as folder:
            path = Path(folder) / "present.md"
            for value, expected in (("색상 존재", 0), ("색상이 있음", 1)):
                path.write_text(table(value), encoding="utf-8")
                result = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True,
                                        encoding="utf-8", env={**os.environ, "PYTHONIOENCODING": "utf-8"})
                self.assertEqual(expected, result.returncode, result.stderr)
                if expected:
                    self.assertIn(":3:cell-1: DOC002", result.stdout)
            result = subprocess.run([sys.executable, str(SCRIPT), str(path.with_name("absent.md"))], capture_output=True)
            self.assertEqual(2, result.returncode)

    def test_git_discovery(self):
        with temporary_workspace() as folder:
            root = Path(folder)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            # Tracked: present/absent. Untracked: included/ignored. Unicode is a separate axis.
            cases = (
                ("tracked-present.md", True, True, False, True),
                ("tracked-absent.md", True, False, False, False),
                ("untracked-included.md", False, True, False, True),
                ("untracked-ignored.md", False, True, True, False),
                ("untracked-한글 문서.md", False, True, False, True),
            )
            expected = set()
            for name, tracked, present, ignored, included in cases:
                path = root / name
                path.write_text(table("색상 존재"), encoding="utf-8")
                if tracked:
                    subprocess.run(["git", "add", name], cwd=root, check=True, capture_output=True)
                if not present:
                    path.unlink()
                if ignored:
                    (root / ".gitignore").write_text(f"{name}\n", encoding="utf-8")
                if included:
                    expected.add(name)
            self.assertEqual(expected, {path.name for path in CHECKER.discover(root)})


if __name__ == "__main__":
    unittest.main()
