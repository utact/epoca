# Sprite Studio 분석

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
  "repository": "https://github.com/JohnKinyanjui/sprite-maker",
  "revision": "9de73a6136a1a045af2e8769349fbadc17dbef69",
  "license": "MIT",
  "stars": 416,
  "last_commit_at": "2026-09-24T22:57:25Z",
  "archived": false,
  "unknowns": {},
  "evidence_level": "code-inspected",
  "evidence": [
    "https://api.github.com/repos/JohnKinyanjui/sprite-maker",
    "https://api.github.com/repos/JohnKinyanjui/sprite-maker/commits/9de73a6136a1a045af2e8769349fbadc17dbef69",
    "https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/README.md",
    "https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/LICENSE",
    "https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/src-tauri/resources/skills/sprite-director/references/physical-motion-contract.md",
    "https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/src-tauri/src/motion_planner/classify.rs",
    "https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/src-tauri/src/motion_planner/plan.rs",
    "https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/src-tauri/src/rig/creature_templates.rs",
    "https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/src-tauri/src/quality/motion_checks.rs",
    "https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/src-tauri/src/quality/analysis.rs",
    "https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/src-tauri/src/pipeline/contract.rs",
    "https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/src-tauri/src/pipeline/contract_retry.rs",
    "https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/src-tauri/src/pipeline/contract_retry_tests.rs",
    "https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/src-tauri/src/pipeline/production_score.rs",
    "https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/src-tauri/src/animations/export.rs",
    "https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/.github/workflows/ci.yml"
  ]
}
```

## 목적과 사용자

AI 생성·리그 편집·애니메이션 검토·자산 보존·내보내기를 제공하는 데스크톱 작업 도구다. 저장소 이름은 `sprite-maker`이며 제품 이름은 Sprite Studio다. [README](https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/README.md)에서 Tauri·Svelte·Rust·SQLite와 외부 에이전트 CLI를 사용하는 구성을 확인했다.

## 핵심 기능

기준 이미지·동작 계획·프레임 생성·정규화·크기 계약·검토·PNG 시트 출력 경로를 제공한다. 생물별 물리적 맥락을 고려하라는 지침과 사족·날개·뱀 형태의 리그 템플릿이 이미 있다. [물리 동작 지침](https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/src-tauri/resources/skills/sprite-director/references/physical-motion-contract.md)과 [생물 리그 템플릿](https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/src-tauri/src/rig/creature_templates.rs)에서 확인했다.

다만 [동작 분류](https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/src-tauri/src/motion_planner/classify.rs)와 [계획 생성](https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/src-tauri/src/motion_planner/plan.rs)에서 읽은 경로는 영어 키워드와 단계 템플릿으로 동작·프레임 수를 정한다. 이 함수가 이미지를 분석해 생물 특성을 인식한다고 해석할 수 없다. 템플릿 선택과 모델의 시각 판단 연결은 추가 확인 대상이다.

## 실행 흐름

사용자가 기준 자산과 동작을 정하면 생성 또는 리그 경로로 프레임을 만든다. 정규화·크기 계약 검토 후 PNG 스트립과 프레임 시간·오프셋 등의 메타정보를 출력한다. [내보내기 진입점](https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/src-tauri/src/animations/export.rs)에서 `ensure_export_allowed` 호출과 이미지·시간 데이터 구성을 확인했다.

크기 계약의 수정은 기본 2회이며 지정값을 1~5회로 제한한다. 정규화·기준선 보정 후에도 실패하면 수정 지침을 만들고 옵션에 따라 생성 제공자를 호출한다. [수정 경로](https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/src-tauri/src/pipeline/contract_retry.rs)에 근거한다. 전체 AI 재시도의 전역 예산이 이 한도와 같다고 판단하지 않는다.

## 하네스 구성

아래 표는 안내·관측·출력 차단·수정·개발 검사 순서다.

| 구성 요소와 연결 | 역할 | 판정 주체와 기준 | 상태와 다음 행동 | 근거 |
| --- | --- | --- | --- | --- |
| 개체·동작 요청 → 물리적 맥락 | Guide | 사람·모델에 대한 규모·접지·타이밍 지침 | 추정 근거와 사용자 표현 허용·자동 강제 범위 미확인 | [동작 지침](https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/src-tauri/resources/skills/sprite-director/references/physical-motion-contract.md) |
| 프레임 하체 영역 → 다리 구분 경고 | Sensor | 코드의 분리 영역·명도 차이 휴리스틱 | 측정 가능한 쌍다리 조건에서 경고·오류·조건 부족 시 검사 목록 공백 가능 | [동작 검사](https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/src-tauri/src/quality/motion_checks.rs)와 [분석 호출](https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/src-tauri/src/quality/analysis.rs) |
| 크기 계약·검토 상태 → 출력 허용 | Gate | 코드의 차단 위반·검토 상태 Verification | 조건부 출력 차단·accepted 상태와 방향 집합의 별도 분기 | [출력 허용 조건](https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/src-tauri/src/pipeline/contract.rs) |
| 계약 위반 → 정규화·생성 요청 | Transformer | 코드의 재검사와 제공자 호출 | 한도 내 결정적 보정·잔여 위반의 수정 지침과 선택적 재생성 | [계약 수정](https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/src-tauri/src/pipeline/contract_retry.rs) |
| 수정 요청 → 상태·로그 검증 | Sensor | 코드의 취소·실패·힌트 Verification | 테스트 assertion과 CI 호출·실행 결과 미확인 | [수정 테스트](https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/src-tauri/src/pipeline/contract_retry_tests.rs)와 [CI 정의](https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/.github/workflows/ci.yml) |

크기 계약에서 정체성 변화·정지 프레임 경고는 차단 위반과 구분한다. 또한 `accepted` 상태에는 출력 허용 분기가 있어 내보내기 성공을 모든 품질 검사 통과로 해석하면 안 된다.

[종합 점수](https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/src-tauri/src/pipeline/production_score.rs)는 완료된 품질 보고서가 없으면 크기 계약 점수를 품질 점수에 대입한다. 평가에서는 `animations_with_quality`와 실제 검사 범위를 함께 읽어야 한다. 점수만 비교하면 미검증 조건이 가려질 수 있다.

## 근거와 한계

첫 조사의 동작 안내·계약·검사·수정·출력 연결 분석을 완료했다. 공개된 아이디어와 코드가 있으므로 생물별 지침 자체를 새 기능의 독창성으로 확정할 수 없다. 반면 지침의 준수율과 사족보행 탐지 성능은 아직 입증하지 않았다.

사람형 쌍다리 휴리스틱을 사족·뱀·날개 개체에 공통 적용할 수 있는지는 별도 Eval이 필요하다. 리그 템플릿의 존재와 다양한 입력에서의 자동 인식·자연스러움은 별개다. 설치·모델 호출·리그 렌더링·원격 CI는 수행하지 않았다. [루트 라이선스](https://github.com/JohnKinyanjui/sprite-maker/blob/9de73a6136a1a045af2e8769349fbadc17dbef69/LICENSE) 외에 제공자와 참조 자산의 사용 조건을 별도로 확인해야 한다.

