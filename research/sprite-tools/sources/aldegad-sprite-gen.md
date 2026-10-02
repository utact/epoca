# sprite-gen 분석

## 기록 정보

```json
{
  "schema_version": 1,
  "recorded_at": "2026-10-02T15:46:41+09:00",
  "status": "complete",
  "inputs": [
    "research/sprite-tools/plan.md"
  ],
  "taxonomy_version": 1,
  "repository": "https://github.com/aldegad/sprite-gen",
  "revision": "73fbd6d94b5df92b4a23848053fa7741dfc9fe6b",
  "license": "Apache-2.0",
  "stars": 2185,
  "last_commit_at": "2026-10-01T22:31:57Z",
  "archived": false,
  "unknowns": {},
  "evidence_level": "code-inspected",
  "evidence": [
    "https://api.github.com/repos/aldegad/sprite-gen",
    "https://api.github.com/repos/aldegad/sprite-gen/commits/73fbd6d94b5df92b4a23848053fa7741dfc9fe6b",
    "https://github.com/aldegad/sprite-gen/blob/73fbd6d94b5df92b4a23848053fa7741dfc9fe6b/README.md",
    "https://github.com/aldegad/sprite-gen/blob/73fbd6d94b5df92b4a23848053fa7741dfc9fe6b/LICENSE",
    "https://github.com/aldegad/sprite-gen/blob/73fbd6d94b5df92b4a23848053fa7741dfc9fe6b/docs/qa-motion.md",
    "https://github.com/aldegad/sprite-gen/blob/73fbd6d94b5df92b4a23848053fa7741dfc9fe6b/sprite_gen/qa/inspect.py",
    "https://github.com/aldegad/sprite-gen/blob/73fbd6d94b5df92b4a23848053fa7741dfc9fe6b/sprite_gen/qa/score.py",
    "https://github.com/aldegad/sprite-gen/blob/73fbd6d94b5df92b4a23848053fa7741dfc9fe6b/sprite_gen/qa/motion.py",
    "https://github.com/aldegad/sprite-gen/blob/73fbd6d94b5df92b4a23848053fa7741dfc9fe6b/sprite_gen/qa/correction_loop.py",
    "https://github.com/aldegad/sprite-gen/blob/73fbd6d94b5df92b4a23848053fa7741dfc9fe6b/tests/qa/test_motion.py",
    "https://github.com/aldegad/sprite-gen/blob/73fbd6d94b5df92b4a23848053fa7741dfc9fe6b/.github/workflows/ci.yml"
  ]
}
```

## 목적과 사용자

참조 이미지에서 게임용 시트나 투명한 동작 루프를 만드는 CLI와 에이전트용 작업 흐름이다. 생성 제공자와 후처리·검토 도구를 묶는다. [README](https://github.com/aldegad/sprite-gen/blob/73fbd6d94b5df92b4a23848053fa7741dfc9fe6b/README.md)에서 목적과 두 생성 경로를 확인했다.

## 핵심 기능

상태별 행 생성 → 배경 제거·프레임 추출 → 아틀라스 합성과 참조 이미지 → 영상 생성 → 프레임 추출 → 루프 선택을 제공한다. 선택적 검토 UI와 색상 변형·엔진용 내보내기도 문서에 명시돼 있다. 이 전체 범위는 문서 확인 수준이며 이번 코드 분석은 검사·점수·수정 반복에 집중했다.

정적 검사에는 프레임 수·색 히스토그램·지각 해시·동작 변화량이 포함된다. [검사 코드](https://github.com/aldegad/sprite-gen/blob/73fbd6d94b5df92b4a23848053fa7741dfc9fe6b/sprite_gen/qa/inspect.py)와 [점수 코드](https://github.com/aldegad/sprite-gen/blob/73fbd6d94b5df92b4a23848053fa7741dfc9fe6b/sprite_gen/qa/score.py)에서 확인했다. 이 지표만으로 관절 구조나 동작 의미가 정확하다고 판정하지 않는다.

## 실행 흐름

행 생성 경로는 기준 이미지와 상태 목록으로 요청·가이드를 준비하고 제공자를 호출한 뒤 추출·합성을 수행한다. 영상 경로는 영상 생성과 FFmpeg·WebP 도구를 사용한다. 제공자 자격 증명과 실행 환경이 필요하며 이번 조사에서는 설치·호출하지 않았다. [경로·설치 설명](https://github.com/aldegad/sprite-gen/blob/73fbd6d94b5df92b4a23848053fa7741dfc9fe6b/README.md)에 근거한다.

별도 검사 명령은 기존 실행 폴더나 프레임 시퀀스를 읽는다. 수정 루프는 검사 보고서·점수·힌트를 저장하고 선택적으로 외부 제공자 명령을 호출한다. [수정 루프](https://github.com/aldegad/sprite-gen/blob/73fbd6d94b5df92b4a23848053fa7741dfc9fe6b/sprite_gen/qa/correction_loop.py)에서 기본 최대 3회·성공 조건·제공자 오류 시 중단을 확인했다.

## 하네스 구성

아래 표는 안내·관측·수정 반복·개발 검사 순서다.

| 구성 요소와 연결 | 역할 | 판정 주체와 기준 | 상태와 다음 행동 | 근거 |
| --- | --- | --- | --- | --- |
| 상태별 미리보기 → 동작 검토 | Guide | 사람 또는 별도 시각 모델의 동작 판정 지침 | 문서상 실패 행 재생성·모든 CLI 경로의 자동 차단 미확인 | [동작 QA 지침](https://github.com/aldegad/sprite-gen/blob/73fbd6d94b5df92b4a23848053fa7741dfc9fe6b/docs/qa-motion.md) |
| 프레임 시퀀스 → 접지 보고서 | Sensor | 코드의 수동 접지 주석·발 영역 조건 Verification | unknown·needs-review·verified 구분·조건 부족 시 보폭 미확정 | [접지 측정](https://github.com/aldegad/sprite-gen/blob/73fbd6d94b5df92b4a23848053fa7741dfc9fe6b/sprite_gen/qa/motion.py) |
| 실행 폴더 → 검사·점수·수정 힌트 | Sensor·Gate·Transformer | 코드의 행별 오류·점수 조건 Verification | 지정 반복 한도 내 외부 명령 호출·오류 시 중단·dry-run과 실제 수정 구분 | [run_loop](https://github.com/aldegad/sprite-gen/blob/73fbd6d94b5df92b4a23848053fa7741dfc9fe6b/sprite_gen/qa/correction_loop.py) |
| 고정 시퀀스 → 측정 검증 | Sensor | 코드의 정상·모호한 접지 사례 Verification | assertion 실패·CI의 pytest 호출 연결 | [접지 테스트](https://github.com/aldegad/sprite-gen/blob/73fbd6d94b5df92b4a23848053fa7741dfc9fe6b/tests/qa/test_motion.py)와 [CI 정의](https://github.com/aldegad/sprite-gen/blob/73fbd6d94b5df92b4a23848053fa7741dfc9fe6b/.github/workflows/ci.yml) |

접지 측정은 같은 발이 닿아 있는 구간과 그 발만 포함하는 ROI를 호출자가 지정해야 한다. 실루엣 아래쪽만 보고 자동으로 발을 식별하지 않는다. `verified`는 이 조건에서 계산한 측정의 상태이지 생물 전체의 자연스러움 합격이 아니다.

수정 루프의 점수는 검사 결과의 오류·경고·유사도에서 산출한다. 동작 QA 문서의 의미 판정이 이 점수에 자동으로 연결된다고 확인하지 못했다. 문서의 BLOCKING 표현과 코드의 실제 종료 조건을 구분한다.

## 근거와 한계

첫 조사의 경로 비교와 검사·수정 반복 분석을 완료했다. 검사 함수·접지 측정·반복 한도와 테스트 정의를 코드로 확인했다. 생성 품질·판정 정확도·재시도 개선율·비용·원격 CI 결과는 미검증이다.

재사용 후보는 프레임 처리·관측값·한도가 있는 수정 반복의 구조다. “한쪽 앞다리를 갑자기 드는 늑대”를 자동 탐지할 수 있는지는 이 코드 분석으로 확인되지 않았다. 동일 개체·보행·행동 의미를 별도 평가해야 한다. [루트 라이선스](https://github.com/aldegad/sprite-gen/blob/73fbd6d94b5df92b4a23848053fa7741dfc9fe6b/LICENSE)와 생성 서비스·모델·참조 자산의 조건은 구분한다.


