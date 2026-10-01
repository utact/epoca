"""Synthetic normal/error records plus regressions from the discarded asset study."""

import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys
import time
import unittest
import uuid
from contextlib import contextmanager
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check-workflow.py"
SPEC = importlib.util.spec_from_file_location("check_workflow", SCRIPT)
CHECKER = importlib.util.module_from_spec(SPEC)
sys.dont_write_bytecode = True
SPEC.loader.exec_module(CHECKER)
SECTIONS = {
    "research/demo/plan.md": ["기록 정보", "조사 질문", "범위와 제외", "후보 선정", "분석 기준", "진행 순서", "완료 조건"],
    "research/demo/sources/example-tool.md": ["기록 정보", "목적과 사용자", "핵심 기능", "실행 흐름", "하네스 구성", "근거와 한계"],
    "research/demo/report.md": ["기록 정보", "조사 범위", "비교 결과", "재사용 후보", "미확인 사항", "다음 결정"],
    "experiments/demo/plan.md": ["기록 정보", "질문과 가설", "입력과 고정 조건", "비교 조건", "실행 순서와 예산", "평가 기준", "완료 조건"],
    "experiments/demo/report.md": ["기록 정보", "실행 범위", "결과", "실패와 제외", "해석", "결정과 한계"],
}
SOURCE = "research/demo/sources/example-tool.md"
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8", "GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "test@example.invalid",
       "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "test@example.invalid"}


@contextmanager
def workspace():
    parent = Path(__file__).resolve().parent
    folder = parent / ("tmp-" + uuid.uuid4().hex)
    folder.mkdir()
    try:
        yield folder
    finally:
        if folder.resolve().parent != parent:
            raise RuntimeError("Test workspace escaped its parent")

        def remove_readonly(function, path, error):
            if not isinstance(error, PermissionError):
                raise error
            os.chmod(path, stat.S_IWRITE)
            function(path)

        for attempt in range(5):
            try:
                shutil.rmtree(folder, onexc=remove_readonly)
                break
            except PermissionError:
                if attempt == 4:
                    raise
                time.sleep(0.1 * (attempt + 1))


def git(root, *args):
    return subprocess.run(["git", "-c", "gc.auto=0", "-c", "maintenance.auto=false", *args], cwd=root, env=ENV, check=True, capture_output=True).stdout.decode("utf-8").strip()


def metadata(name):
    data = {"schema_version": 1, "recorded_at": "2026-10-01T12:00:00+09:00", "status": "planned", "inputs": []}
    if name.endswith("report.md"):
        data["inputs"] = [str(Path(name).with_name("plan.md")).replace("\\", "/")]
    if name == SOURCE:
        data.update(taxonomy_version=1, repository="https://github.com/example/tool", revision="a" * 40,
                    license="MIT", stars=0, last_commit_at="2026-09-30T03:00:00Z", archived=False,
                    unknowns={}, evidence_level="documented", evidence=["https://github.com/example/tool"])
    return data


def record(name, data=None):
    info = metadata(name) if data is None else data
    parts = ["# 합성 검사 사례\n", "## 기록 정보\n\n```json\n" + json.dumps(info, ensure_ascii=False, indent=2) + "\n```\n"]
    parts += [f"## {title}\n\n검사할 조건과 근거를 기록한다.\n" for title in SECTIONS[name][1:]]
    return "\n".join(parts)


def write(root, name, content):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def codes(root, name, text):
    path = write(root, name, text)
    return [issue[1] for issue in CHECKER.check_record(root, path)]


class WorkflowChecks(unittest.TestCase):
    def test_documented_contract_and_diagnostics(self):
        guide = (ROOT / "docs/engineering/research.md").read_text(encoding="utf-8")
        for headings in SECTIONS.values():
            self.assertIn(" → ".join(headings), guide)
        spec = (ROOT / "specs/workflow-checks/spec.md").read_text(encoding="utf-8")
        registered = [line.split("|")[1].strip() for line in spec.splitlines() if line.startswith("| WFL")]
        self.assertEqual(list(CHECKER.MESSAGES), registered)

    def test_all_record_kinds(self):
        with workspace() as root:
            for name in SECTIONS:
                if name.endswith("report.md"):
                    plan = name.replace("report.md", "plan.md")
                    write(root, plan, record(plan))
                with self.subTest(name=name):
                    self.assertEqual([], codes(root, name, record(name)))

    def test_heading_missing_reordered_duplicate_and_empty(self):
        name = "research/demo/plan.md"
        original = record(name)
        cases = [
            original.replace("## 후보 선정", "## 후보 누락"),
            original.replace("## 후보 선정", "## 분석 기준"),
            original.replace("## 후보 선정", "## TEMP").replace("## 분석 기준", "## 후보 선정").replace("## TEMP", "## 분석 기준"),
            original.replace("## 후보 선정\n\n검사할 조건과 근거를 기록한다.", "## 후보 선정\n"),
            original + "\n# 두 번째 제목\n",
        ]
        with workspace() as root:
            for value in cases:
                self.assertIn("WFL002", codes(root, name, value))
            self.assertEqual([], codes(root, name, original + "\n```md\n## 예시 속 제목\n```\n"))
            self.assertIn("WFL002", codes(root, name, original + "\n```md\n닫히지 않은 예시"))

    def test_metadata_fields_and_types(self):
        mutations = [
            ("schema_version", True), ("schema_version", 2), ("taxonomy_version", 2),
            ("recorded_at", "2026-10-01"), ("recorded_at", "2026-10-01T12:00:00"),
            ("recorded_at", "2026-02-30T12:00:00Z"), ("status", "passed"),
            ("repository", "file:///private"), ("repository", "https://example.com/ bad"),
            ("repository", "https://user:secret@example.com/repo"),
            ("revision", "abcdef0"), ("stars", -1), ("stars", True), ("stars", "100"),
            ("archived", 0), ("last_commit_at", "yesterday"), ("license", ""),
            ("inputs", [{"file": "x"}]), ("evidence", []), ("evidence_level", "confirmed"),
        ]
        with workspace() as root:
            for key, value in mutations:
                data = metadata(SOURCE)
                data[key] = value
                with self.subTest(key=key, value=value):
                    self.assertIn("WFL003", codes(root, SOURCE, record(SOURCE, data)))
            data = metadata(SOURCE)
            del data["repository"]
            data["reposistory"] = "https://github.com/example/tool"
            self.assertIn("WFL003", codes(root, SOURCE, record(SOURCE, data)))
            data = metadata(SOURCE)
            data["revision"] = "a" * 64
            self.assertEqual([], codes(root, SOURCE, record(SOURCE, data)))

    def test_unknown_values_need_reasons(self):
        with workspace() as root:
            for field in ("license", "stars", "last_commit_at", "archived"):
                data = metadata(SOURCE)
                data[field] = None
                self.assertIn("WFL003", codes(root, SOURCE, record(SOURCE, data)))
                data["unknowns"][field] = "이번 조회에서 제공하지 않은 값이다."
                self.assertEqual([], codes(root, SOURCE, record(SOURCE, data)))
                data["unknowns"][field] = " "
                self.assertIn("WFL003", codes(root, SOURCE, record(SOURCE, data)))

    def test_duplicate_and_nonstandard_json(self):
        original = record(SOURCE)
        cases = [original.replace('"schema_version": 1,', '"schema_version": 1, "schema_version": 1,'),
                 original.replace('"stars": 0', '"stars": NaN'), original.replace('"stars": 0', '"stars": ')]
        with workspace() as root:
            for value in cases:
                self.assertIn("WFL003", codes(root, SOURCE, value))

    def test_plan_and_local_evidence_links(self):
        name = "experiments/demo/report.md"
        with workspace() as root:
            self.assertIn("WFL004", codes(root, name, record(name)))
            write(root, "experiments/demo/plan.md", record("experiments/demo/plan.md"))
            self.assertEqual([], codes(root, name, record(name)))
            data = metadata(name)
            data["inputs"] = []
            self.assertIn("WFL004", codes(root, name, record(name, data)))
            for value in ("../outside.md", "C:/outside.md", "/outside.md", "./local.md", "dir//local.md", "absent.md"):
                data = metadata(SOURCE)
                data["inputs"] = [value]
                self.assertIn("WFL004", codes(root, SOURCE, record(SOURCE, data)))

    def test_evidence_levels(self):
        with workspace() as root:
            data = metadata(SOURCE)
            data["evidence_level"] = "code-inspected"
            self.assertIn("WFL004", codes(root, SOURCE, record(SOURCE, data)))
            data["evidence"] = ["https://github.com/example/tool/blob/" + "a" * 40 + "/processor.py"]
            self.assertEqual([], codes(root, SOURCE, record(SOURCE, data)))
            data["evidence_level"] = "executed"
            self.assertIn("WFL004", codes(root, SOURCE, record(SOURCE, data)))
            write(root, "experiments/demo/run.log", "synthetic execution evidence")
            data["inputs"] = ["experiments/demo/run.log"]
            self.assertEqual([], codes(root, SOURCE, record(SOURCE, data)))

    def test_symlink_cannot_escape_repository(self):
        with workspace() as root, workspace() as outside:
            target = write(outside, "evidence.md", "external")
            link = root / "linked.md"
            try:
                link.symlink_to(target)
            except OSError:
                self.skipTest("Host does not permit symlink creation")
            data = metadata(SOURCE)
            data["inputs"] = ["linked.md"]
            self.assertIn("WFL004", codes(root, SOURCE, record(SOURCE, data)))

    def test_commit_titles_and_real_regressions(self):
        # Exact titles from the discarded branches; the corrected forms are proposed alternatives.
        for original, corrected in (
            ("Record adaptive sprite study and lossless WebP comparison", "experiment(sprite-encoding): 무손실 WebP 비교 결과 기록"),
            ("Separate asset experiments and define controlled fixture strategy", "docs(asset-pipeline): 비교 조건과 픽스처 기준 정의"),
        ):
            self.assertFalse(CHECKER.valid_commit_title(original))
            self.assertTrue(CHECKER.valid_commit_title(corrected))
        for value in ("docs: 작업 기준 정의", "feat(record-checks): 조사 기록 검사 추가", "fix: 경로 검사 수정"):
            self.assertTrue(CHECKER.valid_commit_title(value))
        for value in ("docs: 작업 기준 정의.", " docs: 작업 기준 정의", "docs:작업 기준 정의", "docs(Bad Scope): 기준 정의", "other: 기준 정의", "docs: English only"):
            self.assertFalse(CHECKER.valid_commit_title(value))

    def test_discovery_and_cli_exit_codes(self):
        with workspace() as root:
            git(root, "init", "-q")
            name = "research/demo/plan.md"
            good = write(root, name, record(name))
            write(root, ".gitignore", "research/cache/\n")
            write(root, "research/cache/invalid.md", "ignored")
            self.assertEqual([good], CHECKER.discover(root))
            git(root, "add", name)
            self.assertEqual([good], CHECKER.discover(root))
            command = [sys.executable, str(SCRIPT), "--root", str(root)]
            result = subprocess.run(command, env=ENV, capture_output=True, encoding="utf-8")
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            message = write(root, "commit-message.txt", "docs: 기준 정의\n\n- 역할별 문서 위치 추가\n")
            result = subprocess.run(command + ["--message-file", str(message)], env=ENV, capture_output=True)
            self.assertEqual(0, result.returncode)
            message.write_text("bad title\n", encoding="utf-8")
            result = subprocess.run(command + ["--message-file", str(message)], env=ENV, capture_output=True)
            self.assertEqual(1, result.returncode)
            self.assertIn(b"WFL005", result.stdout)
            write(root, "research/demo/notes.md", "unregistered record")
            result = subprocess.run(command, env=ENV, capture_output=True, encoding="utf-8")
            self.assertEqual(1, result.returncode)
            self.assertIn("WFL001", result.stdout)
            result = subprocess.run(command + ["--message-file", str(root / "absent.txt")], env=ENV, capture_output=True)
            self.assertEqual(2, result.returncode)
            good.unlink()
            self.assertNotIn(good, CHECKER.discover(root))

    def test_commit_range_ignores_old_history(self):
        with workspace() as root:
            git(root, "init", "-q")
            git(root, "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "Initial commit")
            base = git(root, "rev-parse", "HEAD")
            git(root, "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "docs: 기준 정의")
            self.assertEqual(["docs: 기준 정의"], [title for _, title in CHECKER.commit_titles(root, base, "HEAD")])
            git(root, "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "bad commit")
            command = [sys.executable, str(SCRIPT), "--root", str(root), "--commit-base", base]
            result = subprocess.run(command, env=ENV, capture_output=True, encoding="utf-8")
            self.assertEqual(1, result.returncode)
            self.assertIn("WFL005", result.stdout)
            self.assertEqual(1, len(CHECKER.commit_titles(root, "0" * 40, "HEAD")))
            result = subprocess.run(command[:-1] + ["missing-ref"], env=ENV, capture_output=True)
            self.assertEqual(2, result.returncode)

    def test_commit_body_normal_and_failures(self):
        title = "docs: 기준 정의"
        for message in (title, title + "\n\n- 역할별 문서 위치 추가\n- 입력 경로 검사 통과\n",
                        title + "\n\n- 참고: https://example.com/config?v=1.2\n",
                        title + "\n\n- 경로 연결 수정\n\nCo-Authored-By: Kim <kim@example.invalid>\n",
                        title + "\n\nCo-Authored-By: Kim <kim@example.invalid>\n"):
            with self.subTest(message=message):
                self.assertEqual([], CHECKER.check_commit_message(message))
        cases = (
            title + "\n- 역할별 문서 위치 추가",
            title + "\nCo-Authored-By: Kim <kim@example.invalid>",
            title + "\n\n- 역할별 문서 위치 추가\n\n- 입력 경로 검사 통과",
            title + "\n\n역할별 문서 위치를 추가했다. 검사를 통과했다.",
            title + "\n\n- 역할별 문서 위치 추가\n  두 번째 줄",
            title + "\n\n- 기준 정의",
            title + "\n\n- 연결 수정\n- 연결 수정",
            title + "\n\n- 연결 수정\nCo-Authored-By: Kim <kim@example.invalid>",
            title + "\n\n- 연결 수정\n\nCo-Authored-By: Codex <codex@example.invalid>",
            title + "\n\n- Generated with Claude",
            title + "\n\n- https://chatgpt.com/codex/tasks/example",
        )
        for message in cases:
            with self.subTest(message=message):
                self.assertIn("WFL006", [code for _, code, _ in CHECKER.check_commit_message(message)])

    def test_real_commit_body_regression(self):
        # Exact message from 5593bd3 before the user-requested history rewrite.
        message = ("feat(workflow-checks): 기술 조사·실험 규약과 검사 추가\n\n"
                   "커밋 규칙, 문서 책임·목차·메타정보, 기록 검사기와 회귀 테스트 및 CI를 정의한다. "
                   "기존 스프라이트 도구 조사는 제공 범위와 구현 근거를 기준으로 구성하고, 추가 기능 가설과 EPOCA 적용은 별도 개발 계획에 둔다. "
                   "문서 15개 검사와 조사 기록·로컬 링크 검사 및 별도 문체·의미 검토를 완료했다. "
                   "구현 테스트는 27개 통과, Windows 링크 생성 권한으로 1개 생략했다. 원격 CI는 미확인이다.")
        self.assertTrue(CHECKER.valid_commit_title(message.splitlines()[0]))
        self.assertIn("WFL006", [code for _, code, _ in CHECKER.check_commit_message(message)])

    def test_full_message_in_git_range(self):
        with workspace() as root:
            git(root, "init", "-q")
            git(root, "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "Initial commit")
            base = git(root, "rev-parse", "HEAD")
            message = "docs: 기준 정의\n\n- 역할별 문서 위치 추가\n- 입력 경로 검사 통과"
            git(root, "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", message)
            sha, actual = CHECKER.commit_messages(root, base, "HEAD")[0]
            self.assertEqual(message, actual.strip())
            self.assertEqual([], CHECKER.check_commit_message(actual))
            self.assertEqual("docs: 기준 정의", CHECKER.commit_titles(root, base, "HEAD")[0][1])
            bad = "docs: 오류 사례\n\n연결을 고쳤다. 검사도 했다."
            git(root, "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", bad)
            command = [sys.executable, str(SCRIPT), "--root", str(root), "--commit-base", base]
            result = subprocess.run(command, env=ENV, capture_output=True, encoding="utf-8")
            self.assertEqual(1, result.returncode)
            self.assertIn("WFL006", result.stdout)
            self.assertNotIn("WFL005", result.stdout)

    def test_local_link_targets_and_anchors(self):
        with workspace() as root:
            write(root, "docs/target.md", "# 문서\n\n## 중복 제목\n\n## 중복 제목\n\n## `Code`와 **표현**\n\n<a id=\"custom-id\"></a>\n")
            write(root, "docs/image.png", "synthetic")
            write(root, "docs/file name.md", "# 공백 파일\n")
            write(root, "docs/file(v1).md", "# 괄호 파일\n")
            path = write(root, "docs/source.md", "# 원본\n\n"
                         "[정상](target.md#중복-제목) [중복](target.md#중복-제목-1)\n"
                         "[서식](target.md#code와-표현) [명시](target.md#custom-id)\n"
                         "![이미지](image.png) [인코딩](file%20name.md) [공백](<file name.md>)\n"
                         "[괄호](file(v1).md) [외부](https://example.com/missing.md#missing)\n"
                         "[현재](#원본)\n")
            self.assertEqual([], CHECKER.check_links(root, path))
            for target in ("absent.md", "target.md#없는-절", "target.md#중복-제목-2", "../../outside.md"):
                path.write_text(f"# 원본\n\n[오류]({target})\n", encoding="utf-8")
                self.assertEqual("WFL007", CHECKER.check_links(root, path)[0][1])

    def test_link_examples_are_ignored_and_prose_wrap_is_unrestricted(self):
        with workspace() as root:
            path = write(root, "README.md", "# 문서\n\n"
                         "문장 하나다. 문장 둘이다.\n\n- 한 항목이다. 여러 문장이다.\n\n"
                         "`[예시](missing.md)`\n\n```md\n[예시](missing.md)\n```\n"
                         "<!-- [예시](missing.md) -->\n"
                         "[참조형][missing]\n\n[missing]: missing.md\n")
            self.assertEqual([], CHECKER.check_links(root, path))
            path.write_text(path.read_text(encoding="utf-8") + "\n[실제](missing.md)\n", encoding="utf-8")
            self.assertEqual(1, len(CHECKER.check_links(root, path)))

    def test_markdown_discovery_and_link_cli(self):
        with workspace() as root:
            git(root, "init", "-q")
            write(root, ".gitignore", ".cache/\n")
            write(root, ".cache/ignored.md", "[ignored](missing.md)")
            path = write(root, "README.md", "# 문서\n[broken](missing.md)\n")
            self.assertEqual([path], CHECKER.markdown_files(root))
            result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root)], env=ENV, capture_output=True, encoding="utf-8")
            self.assertEqual(1, result.returncode)
            self.assertIn("WFL007", result.stdout)


if __name__ == "__main__":
    unittest.main()
