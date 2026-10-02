# Pixelorama 분석

## 기록 정보

```json
{
  "schema_version": 1,
  "recorded_at": "2026-10-02T15:42:54+09:00",
  "status": "complete",
  "inputs": [
    "research/sprite-tools/plan.md"
  ],
  "taxonomy_version": 1,
  "repository": "https://github.com/Orama-Interactive/Pixelorama",
  "revision": "bb74e9c0f9e225730a0bdc597bbbe242251b894e",
  "license": "MIT",
  "stars": 10439,
  "last_commit_at": "2026-10-01T10:39:47Z",
  "archived": false,
  "unknowns": {},
  "evidence_level": "code-inspected",
  "evidence": [
    "https://api.github.com/repos/Orama-Interactive/Pixelorama",
    "https://api.github.com/repos/Orama-Interactive/Pixelorama/commits/bb74e9c0f9e225730a0bdc597bbbe242251b894e",
    "https://github.com/Orama-Interactive/Pixelorama/blob/bb74e9c0f9e225730a0bdc597bbbe242251b894e/README.md",
    "https://github.com/Orama-Interactive/Pixelorama/blob/bb74e9c0f9e225730a0bdc597bbbe242251b894e/LICENSE",
    "https://github.com/Orama-Interactive/Pixelorama/blob/bb74e9c0f9e225730a0bdc597bbbe242251b894e/src/Main.gd",
    "https://github.com/Orama-Interactive/Pixelorama/blob/bb74e9c0f9e225730a0bdc597bbbe242251b894e/src/Autoload/Export.gd",
    "https://github.com/Orama-Interactive/Pixelorama/blob/bb74e9c0f9e225730a0bdc597bbbe242251b894e/.github/workflows/static-checks.yml"
  ]
}
```

## 목적과 사용자

픽셀 아트를 직접 제작·수정하는 사용자를 위한 편집기다. 레이어·프레임·타임라인·어니언 스킨을 제공한다. 생성 모델이나 생물 동작 판정기로 분류하지 않는다. [README](https://github.com/Orama-Interactive/Pixelorama/blob/bb74e9c0f9e225730a0bdc597bbbe242251b894e/README.md)에서 목적과 지원 기능을 확인했다.

## 핵심 기능

타임라인 편집·프레임 태그·팔레트·이미지 효과와 시트·애니메이션 내보내기를 제공한다. CLI에도 프레임 범위·배율·레이어 분리·JSON 출력 인자가 있다. [CLI 등록 코드](https://github.com/Orama-Interactive/Pixelorama/blob/bb74e9c0f9e225730a0bdc597bbbe242251b894e/src/Main.gd)에서 인자 연결을 확인했다.

`--json`의 출력은 프로젝트 직렬화 데이터다. 이를 바로 PixiJS용 아틀라스 메타정보로 간주하면 안 된다. [내보내기 코드](https://github.com/Orama-Interactive/Pixelorama/blob/bb74e9c0f9e225730a0bdc597bbbe242251b894e/src/Autoload/Export.gd)의 `project.serialize()` 호출에서 확인했다.

## 실행 흐름

프로젝트의 프레임과 레이어를 선택한 뒤 레이어 합성·시트 배치 또는 애니메이션 처리를 거쳐 파일을 저장한다. 애니메이션 처리에서는 프로젝트 FPS와 프레임별 지속 시간을 사용한다. 영상 출력에는 FFmpeg를 호출한다. 읽은 버전의 소스 실행 조건은 README의 Godot 버전을 따르며 설치나 실행은 하지 않았다.

## 하네스 구성

아래 표는 편집·내보내기·개발 검사 순서다. 상태는 코드의 분기이며 이번 조사에서 발생시킨 실행 결과가 아니다.

| 구성 요소와 연결 | 역할 | 판정 주체와 기준 | 상태와 다음 행동 | 근거 |
| --- | --- | --- | --- | --- |
| 타임라인·어니언 스킨 → 프레임 수정 | Guide·Sensor·Transformer | 사람의 재생 확인과 수동 수정 | 사람의 반복 검토와 수동 수정 | [편집 기능 설명](https://github.com/Orama-Interactive/Pixelorama/blob/bb74e9c0f9e225730a0bdc597bbbe242251b894e/README.md) |
| 합성 프레임 → 파일 저장 | Transformer·Sensor·Gate | 코드의 경로·파일명·저장 결과 Verification | 잘못된 경로·저장 실패 시 중단·덮어쓰기 확인 경로는 호출 옵션에 따라 적용 | [export_processed_images](https://github.com/Orama-Interactive/Pixelorama/blob/bb74e9c0f9e225730a0bdc597bbbe242251b894e/src/Autoload/Export.gd) |
| 변경 코드 → 정적 검사 | Sensor | 코드 형식·린트·철자 Verification | 검사 실패는 CI 결과로 전달·필수 병합 조건 미확인 | [정적 검사 워크플로](https://github.com/Orama-Interactive/Pixelorama/blob/bb74e9c0f9e225730a0bdc597bbbe242251b894e/.github/workflows/static-checks.yml) |

내보내기 실패를 보고하는 코드와 동작의 자연스러움을 판정하는 코드는 다른 책임이다. 읽은 정적 검사 워크플로에는 생성 결과의 자연스러움을 평가하는 단계가 없다.

## 근거와 한계

첫 조사의 편집·내보내기 경로 분석을 완료했다. CLI 인자와 저장 경로는 코드로 확인했고 편집 기능 전반은 문서로 확인했다. GUI 조작·포맷 왕복 변환·결과 이미지와 CI 실행 상태는 미검증이다.

재사용 후보는 수동 수정 기준선과 내보내기 어댑터다. 엔진별 메타정보 변환과 프레임 시간 보존은 후속 실험에서 확인해야 한다. [루트 라이선스](https://github.com/Orama-Interactive/Pixelorama/blob/bb74e9c0f9e225730a0bdc597bbbe242251b894e/LICENSE)를 확인했으며 포함된 애드온과 외부 입력 에셋의 조건은 개별 확인 대상이다.

