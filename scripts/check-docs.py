"""Check bounded Markdown table rules from docs/workflow.md (standard library only)."""

import argparse
import re
import subprocess
import sys
from pathlib import Path


FORM_COLUMNS = (
    "present_nominal", "present_plain", "present_polite",
    "past_nominal", "past_plain", "past_polite",
)
# Each value has six entries in FORM_COLUMNS order; '/' separates variants within an entry.
PREDICATE_FORMS = {
    "되다": ("됨", "된다", "됩니다", "되었음/됐음", "되었다/됐다", "되었습니다/됐습니다"),
    "않다": ("않음", "않는다", "않습니다", "않았음", "않았다", "않았습니다"),
    "없다": ("없음", "없다", "없습니다", "없었음", "없었다", "없었습니다"),
    "이다": ("임", "이다", "입니다", "이었음/였음", "이었다/였다", "이었습니다/였습니다"),
    "있다": ("있음", "있다", "있습니다", "있었음", "있었다", "있었습니다"),
    "하다": ("함", "한다", "합니다", "하였음/했음", "하였다/했다", "하였습니다/했습니다"),
}


def ending_pattern():
    patterns = []
    for predicate, forms in PREDICATE_FORMS.items():
        if len(forms) != len(FORM_COLUMNS) or any(not form for form in forms):
            raise ValueError(f"Incomplete predicate forms: {predicate}")
        for form in forms:
            for ending in form.split("/"):
                # Require a word boundary to avoid matching short forms inside ordinary nouns.
                boundary = r"(?<!\S)" if len(ending) == 1 or ending == "이다" else ""
                patterns.append(boundary + re.escape(ending))
    return re.compile("(?:" + "|".join(patterns) + ")$")


ENDINGS = ending_pattern()
MESSAGES = {
    "DOC001": "표 셀 끝의 구두점을 생략하고 명사구로 표현하세요.",
    "DOC002": "서술형 종결 대신 상태·성질·행위의 명사구로 표현하세요.",
}


def cells(line):
    """Split a top-level pipe row, retaining escaped pipes inside cells."""
    if line.startswith(("    ", "\t", ">")) or "|" not in line:
        return []
    parts = re.split(r"(?<!\\)(?:\\\\)*\|", line.strip())
    if parts[0] == "":
        parts.pop(0)
    if parts and parts[-1] == "":
        parts.pop()
    return [part.strip() for part in parts]


def prose(cell):
    # Keep a placeholder so prose before trailing code is not mistaken for the cell ending.
    text = re.sub(r"(`+).*?\1", " CODE ", cell)
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\[[^\]]*\]", r"\1", text)
    return re.sub(r"[*_~]", "", text).strip()


def check_text(text):
    lines = text.splitlines()
    rows = []
    fence = None
    for line in lines:
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                if not marker[2].strip():
                    fence = None
            rows.append([])
            continue
        if marker:
            fence = marker[1]
            rows.append([])
            continue
        rows.append(cells(line))

    table_rows = set()
    for index in range(1, len(rows)):
        row = rows[index]
        if row and all(re.fullmatch(r":?-{3,}:?", cell) for cell in row):
            if len(rows[index - 1]) != len(row):
                continue
            table_rows.add(index - 1)
            following = index + 1
            while following < len(rows) and rows[following]:
                table_rows.add(following)
                following += 1

    issues = []
    for index in sorted(table_rows):
        for column, cell in enumerate(rows[index], 1):
            value = prose(cell)
            if re.search(r"[.!?。！？]$", value):
                issues.append((index + 1, column, "DOC001"))
            if ENDINGS.search(value.rstrip(".!?。！？")):
                issues.append((index + 1, column, "DOC002"))
    return issues


def discover(root):
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=root, check=True, capture_output=True,
    )
    names = set(result.stdout.decode("utf-8").split("\0"))
    return sorted(
        root / name for name in names
        if name.lower().endswith(".md") and (root / name).is_file()
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        paths = args.paths or discover(root)
        count = 0
        for path in paths:
            for line, column, code in check_text(path.read_text(encoding="utf-8-sig")):
                print(f"{path}:{line}:cell-{column}: {code} {MESSAGES[code]}")
                count += 1
    except (OSError, UnicodeError, subprocess.CalledProcessError) as error:
        print(f"문서 검사 실행 실패: {error}", file=sys.stderr)
        return 2
    if count:
        print(f"문서 검사 실패: {count}건")
        return 1
    print(f"문서 {len(paths)}개 자동 검사 통과. 문체·의미 검토는 별도로 수행하세요.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
