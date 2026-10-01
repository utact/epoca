"""Validate research/experiment records and selected commit titles (stdlib only)."""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit


SECTIONS = {
    "research-plan": ("기록 정보", "조사 질문", "범위와 제외", "후보 선정", "분석 기준", "진행 순서", "완료 조건"),
    "source": ("기록 정보", "목적과 사용자", "핵심 기능", "실행 흐름", "하네스 구성", "근거와 한계"),
    "research-report": ("기록 정보", "조사 범위", "비교 결과", "재사용 후보", "미확인 사항", "다음 결정"),
    "experiment-plan": ("기록 정보", "질문과 가설", "입력과 고정 조건", "비교 조건", "실행 순서와 예산", "평가 기준", "완료 조건"),
    "experiment-report": ("기록 정보", "실행 범위", "결과", "실패와 제외", "해석", "결정과 한계"),
}
COMMON_FIELDS = {"schema_version", "recorded_at", "status", "inputs"}
SOURCE_FIELDS = {
    "taxonomy_version", "repository", "revision", "license", "stars",
    "last_commit_at", "archived", "unknowns", "evidence_level", "evidence",
}
UNKNOWN_FIELDS = {"license", "stars", "last_commit_at", "archived"}
MESSAGES = {
    "WFL001": "등록된 기록 경로가 아닙니다.",
    "WFL002": "제목·절 순서·본문을 확인하세요.",
    "WFL003": "메타정보의 필드·값·자료형을 확인하세요.",
    "WFL004": "계획·입력·고정 근거의 연결을 확인하세요.",
    "WFL005": "커밋 제목을 type(scope): 한국어 요약 형식으로 작성하세요. scope는 선택입니다.",
}
KEBAB = r"[a-z0-9]+(?:-[a-z0-9]+)*"
TITLE = re.compile(rf"^(?:chore|docs|experiment|feat|fix|perf|refactor|test)(?:\({KEBAB}\))?: \S(?:.*\S)?$")


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True).stdout.decode("utf-8")


def discover(root):
    names = set(git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard",
                    "--", "research", "experiments").split("\0"))
    return sorted(root / name for name in names if name.lower().endswith(".md") and (root / name).is_file())


def kind_for(name):
    if re.fullmatch(rf"research/{KEBAB}/sources/{KEBAB}\.md", name):
        return "source"
    match = re.fullmatch(rf"(research|experiments)/{KEBAB}/(plan|report)\.md", name)
    if match:
        return f"{'research' if match[1] == 'research' else 'experiment'}-{match[2]}"
    return None


def split_sections(text):
    headings, contents, titles = [], [], []
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if contents:
                contents[-1].append(line)
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            continue
        if marker:
            fence = marker[1]
        elif re.match(r"^# \S", line):
            titles.append(number)
            continue
        elif line.startswith("## "):
            headings.append((number, line[3:].strip()))
            contents.append([])
            continue
        if contents:
            contents[-1].append(line)
    return titles, headings, ["\n".join(body).strip() for body in contents], fence


def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"중복 JSON 키: {key}")
        obj[key] = value
    return obj


def https_url(value):
    if not isinstance(value, str) or re.search(r"\s", value):
        return False
    try:
        parts = urlsplit(value)
        return parts.scheme == "https" and bool(parts.hostname) and not parts.username and not parts.password
    except ValueError:
        return False


def timestamp(value):
    if not isinstance(value, str) or "T" not in value:
        return False
    try:
        return datetime.fromisoformat(value).utcoffset() is not None
    except ValueError:
        return False


def string_list(value):
    return isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value) and len(set(value)) == len(value)


def input_file(root, value):
    # Reject absolute/parent paths even when they happen to resolve inside this checkout.
    if "\\" in value or ":" in value or value.startswith("/") or any(part in {"", ".", ".."} for part in value.split("/")):
        return False
    target = (root / value).resolve()
    return target.is_relative_to(root.resolve()) and target.is_file()


def check_record(root, path):
    name = path.relative_to(root).as_posix()
    if path.name == "README.md":
        return []
    kind = kind_for(name)
    if not kind:
        return [(1, "WFL001", name)]
    text = path.read_text(encoding="utf-8-sig")
    issues = []

    def issue(code, detail, line=1):
        issues.append((line, code, detail))

    titles, headings, bodies, unclosed = split_sections(text)
    if len(titles) != 1 or not headings or titles[0] > headings[0][0] or unclosed:
        issue("WFL002", "절 앞의 제목 1개와 닫힌 코드 블록 필요")
    if tuple(label for _, label in headings) != SECTIONS[kind]:
        issue("WFL002", "기대 순서: " + " → ".join(SECTIONS[kind]))
    for (line, label), body in zip(headings, bodies):
        if not body or not re.sub(r"(?m)^#{3,}.*$", "", body).strip():
            issue("WFL002", f"빈 절: {label}", line)
    if not headings or headings[0][1] != "기록 정보":
        return issues
    metadata = re.fullmatch(r"```json\s*\n(.*?)\n```", bodies[0], re.S)
    if not metadata:
        issue("WFL003", "기록 정보 절에 JSON 코드 블록 하나 필요", headings[0][0])
        return issues
    try:
        data = json.loads(metadata[1], object_pairs_hook=unique_object,
                          parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"비표준 JSON 값: {value}")))
    except (ValueError, TypeError) as error:
        issue("WFL003", str(error), headings[0][0])
        return issues
    if not isinstance(data, dict):
        issue("WFL003", "JSON 객체 필요")
        return issues
    fields = COMMON_FIELDS | (SOURCE_FIELDS if kind == "source" else set())
    if set(data) != fields:
        issue("WFL003", f"누락={sorted(fields - set(data))}, 미등록={sorted(set(data) - fields)}")
    if type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        issue("WFL003", "schema_version: 정수 1 필요")
    if not timestamp(data.get("recorded_at")):
        issue("WFL003", "recorded_at: 시간대 포함 ISO 8601 시각 필요")
    if data.get("status") not in ("planned", "in-progress", "complete", "incomplete"):
        issue("WFL003", "status: 등록 상태 필요")
    inputs = data.get("inputs")
    if not string_list(inputs):
        issue("WFL003", "inputs: 중복 없는 파일 경로 목록 필요")
        inputs = []
    for value in inputs:
        if not input_file(root, value):
            issue("WFL004", f"존재하는 저장소 내부 입력 필요: {value}")
    if kind.endswith("report"):
        expected = path.with_name("plan.md").relative_to(root).as_posix()
        if expected not in inputs:
            issue("WFL004", f"보고서의 계획 연결 필요: {expected}")
    if kind != "source":
        return issues

    if type(data.get("taxonomy_version")) is not int or data["taxonomy_version"] != 1:
        issue("WFL003", "taxonomy_version: 정수 1 필요")
    if not https_url(data.get("repository")):
        issue("WFL003", "repository: 원본 HTTPS URL 필요")
    revision = data.get("revision")
    if not isinstance(revision, str) or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", revision):
        issue("WFL003", "revision: 전체 Git 커밋 해시 필요")
    unknowns = data.get("unknowns")
    nulls = {field for field in UNKNOWN_FIELDS if field in data and data[field] is None}
    if not isinstance(unknowns, dict) or set(unknowns) != nulls or any(not isinstance(v, str) or not v.strip() for v in unknowns.values()):
        issue("WFL003", "unknowns: null 필드마다 비어 있지 않은 이유 필요")
    license_name = data.get("license")
    if license_name is not None and (not isinstance(license_name, str) or not license_name.strip()):
        issue("WFL003", "license: 비어 있지 않은 설명 또는 null 필요")
    stars = data.get("stars")
    if stars is not None and (type(stars) is not int or stars < 0):
        issue("WFL003", "stars: 비음수 정수 또는 null 필요")
    if data.get("last_commit_at") is not None and not timestamp(data["last_commit_at"]):
        issue("WFL003", "last_commit_at: 시간대 포함 시각 또는 null 필요")
    if data.get("archived") is not None and type(data["archived"]) is not bool:
        issue("WFL003", "archived: boolean 또는 null 필요")
    level, evidence = data.get("evidence_level"), data.get("evidence")
    if level not in ("documented", "code-inspected", "executed"):
        issue("WFL003", "evidence_level: 등록 확인 수준 필요")
    if not string_list(evidence) or not evidence or not all(https_url(url) for url in evidence):
        issue("WFL003", "evidence: 중복 없는 HTTPS 근거 URL 목록 필요")
        evidence = []
    if level in ("code-inspected", "executed") and not any(isinstance(revision, str) and revision in urlsplit(url).path.split("/") for url in evidence):
        issue("WFL004", "코드·실행 확인에는 동일 커밋의 고정 URL 필요")
    if level == "executed" and not inputs:
        issue("WFL004", "실행 확인에는 로컬 실행 증거 입력 필요")
    return issues


def valid_commit_title(title):
    return bool(TITLE.fullmatch(title) and re.search(r"[가-힣]", title) and not re.search(r"[.!?。！？]$", title))


def commit_titles(root, base, head):
    # Resolve options to commit hashes before passing them to the range query.
    head_hash = git(root, "rev-parse", "--verify", "--end-of-options", head + "^{commit}").strip()
    if re.fullmatch(r"0{40}|0{64}", base):
        args = [head_hash, "-1"]
    else:
        base_hash = git(root, "rev-parse", "--verify", "--end-of-options", base + "^{commit}").strip()
        args = [base_hash + ".." + head_hash]
    output = git(root, "log", "--no-merges", "--format=%H%x00%s", *args)
    return [tuple(line.split("\0", 1)) for line in output.splitlines()]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--commit-base")
    parser.add_argument("--commit-head", default="HEAD")
    parser.add_argument("--message-file", type=Path)
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve()
        paths = discover(root)
        count, records = 0, 0
        for path in paths:
            if path.name != "README.md":
                records += 1
            for line, code, detail in check_record(root, path):
                print(f"{path.relative_to(root)}:{line}: {code} {MESSAGES[code]} {detail}")
                count += 1
        messages = commit_titles(root, args.commit_base, args.commit_head) if args.commit_base else []
        if args.message_file:
            lines = args.message_file.read_text(encoding="utf-8-sig").splitlines()
            messages.append((str(args.message_file), lines[0] if lines else ""))
        for name, title in messages:
            if not valid_commit_title(title):
                print(f"{name}:1: WFL005 {MESSAGES['WFL005']} 관측: {title!r}")
                count += 1
    except (OSError, UnicodeError, subprocess.CalledProcessError) as error:
        print(f"작업 기록 검사 실행 오류: {error}", file=sys.stderr)
        return 2
    print(f"기록 {records}개·커밋 메시지 {len(messages)}개 검사, 위반 {count}건. 의미·근거 검토는 별도 수행.")
    return 1 if count else 0


if __name__ == "__main__":
    sys.exit(main())
