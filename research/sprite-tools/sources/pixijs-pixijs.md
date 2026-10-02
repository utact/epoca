# PixiJS 분석

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
  "repository": "https://github.com/pixijs/pixijs",
  "revision": "5b41ee37fd36c61e089113345a8f12cf1c3323cf",
  "license": "MIT",
  "stars": 48257,
  "last_commit_at": "2026-10-01T21:38:27Z",
  "archived": false,
  "unknowns": {},
  "evidence_level": "code-inspected",
  "evidence": [
    "https://api.github.com/repos/pixijs/pixijs",
    "https://api.github.com/repos/pixijs/pixijs/commits/5b41ee37fd36c61e089113345a8f12cf1c3323cf",
    "https://github.com/pixijs/pixijs/blob/5b41ee37fd36c61e089113345a8f12cf1c3323cf/README.md",
    "https://github.com/pixijs/pixijs/blob/5b41ee37fd36c61e089113345a8f12cf1c3323cf/LICENSE",
    "https://github.com/pixijs/pixijs/blob/5b41ee37fd36c61e089113345a8f12cf1c3323cf/src/spritesheet/Spritesheet.ts",
    "https://github.com/pixijs/pixijs/blob/5b41ee37fd36c61e089113345a8f12cf1c3323cf/src/scene/sprite-animated/AnimatedSprite.ts",
    "https://github.com/pixijs/pixijs/blob/5b41ee37fd36c61e089113345a8f12cf1c3323cf/src/scene/sprite-animated/__tests__/AnimatedSprite.test.ts",
    "https://github.com/pixijs/pixijs/blob/5b41ee37fd36c61e089113345a8f12cf1c3323cf/.github/workflows/pull-unit.yml",
    "https://github.com/pixijs/pixijs/blob/5b41ee37fd36c61e089113345a8f12cf1c3323cf/.github/actions/unit/action.yml"
  ]
}
```

## 목적과 사용자

브라우저에서 2D 그래픽을 표시하는 렌더링 라이브러리다. 생성 결과를 게임 코드와 연결해 재생하는 단계의 후보이며 이미지 생성이나 자연스러움 평가를 담당하지 않는다. [README](https://github.com/pixijs/pixijs/blob/5b41ee37fd36c61e089113345a8f12cf1c3323cf/README.md)에서 자산 로딩과 렌더러의 범위를 확인했다.

## 핵심 기능

`Spritesheet`는 아틀라스 사각형·회전·잘리기 전 크기·트리밍 오프셋·기본 앵커를 텍스처 객체로 변환한다. `animations`는 프레임 이름의 순서 목록으로 읽는다. [시트 파서](https://github.com/pixijs/pixijs/blob/5b41ee37fd36c61e089113345a8f12cf1c3323cf/src/spritesheet/Spritesheet.ts)에서 확인했다.

`AnimatedSprite`는 텍스처 배열 또는 텍스처와 지속 시간의 배열을 재생한다. 프레임별 시간·반복·완료·프레임 변경 이벤트와 선택적인 앵커 갱신을 제공한다. [재생 구현](https://github.com/pixijs/pixijs/blob/5b41ee37fd36c61e089113345a8f12cf1c3323cf/src/scene/sprite-animated/AnimatedSprite.ts)에서 확인했다. 시트의 애니메이션 이름 목록만으로 프레임별 시간이 전달된다고 가정하지 않는다.

## 실행 흐름

이미지와 JSON을 로드한 뒤 시트를 해석해 텍스처를 만든다. 게임이 상태에 맞는 프레임 목록과 시간을 연결하고 ticker로 재생을 갱신한다. `updateAnchor`는 기본적으로 꺼져 있어 메타정보의 앵커 사용 정책을 정해야 한다. 재생 완료 이벤트와 실제 공격 판정 시점의 연결은 게임 코드의 책임이다.

읽은 버전은 기본 개발 브랜치의 고정 커밋이다. 실행 실험에서는 배포 버전·브라우저·렌더러·기기 조건을 다시 고정해야 한다.

## 하네스 구성

아래 표는 파싱·재생·개발 검사 순서다.

| 구성 요소와 연결 | 역할 | 판정 주체와 기준 | 상태와 다음 행동 | 근거 |
| --- | --- | --- | --- | --- |
| 아틀라스 메타정보 → 텍스처 | Transformer | 코드의 필드 해석 | 파싱 후 텍스처 생성·입력 의미 검증은 호출자 책임 | [Spritesheet](https://github.com/pixijs/pixijs/blob/5b41ee37fd36c61e089113345a8f12cf1c3323cf/src/spritesheet/Spritesheet.ts) |
| 텍스처·시간 → 표시 프레임 | Transformer·Sensor | 코드의 시간 진행과 재생 상태 | 완료·프레임 변경·반복 이벤트·게임 상태 전환은 호출자 담당 | [AnimatedSprite](https://github.com/pixijs/pixijs/blob/5b41ee37fd36c61e089113345a8f12cf1c3323cf/src/scene/sprite-animated/AnimatedSprite.ts) |
| 변경 코드 → 테스트 | Sensor | 코드의 재생 동작 Verification | 테스트 정의와 CI 호출 확인·실제 실행·필수 병합 조건 미확인 | [재생 테스트](https://github.com/pixijs/pixijs/blob/5b41ee37fd36c61e089113345a8f12cf1c3323cf/src/scene/sprite-animated/__tests__/AnimatedSprite.test.ts) |

[PR 워크플로](https://github.com/pixijs/pixijs/blob/5b41ee37fd36c61e089113345a8f12cf1c3323cf/.github/workflows/pull-unit.yml)에서 [공통 검사 액션](https://github.com/pixijs/pixijs/blob/5b41ee37fd36c61e089113345a8f12cf1c3323cf/.github/actions/unit/action.yml)을 호출해 단위 테스트를 실행하도록 연결돼 있다. 테스트의 존재는 실제 EPOCA 장면의 성능 평가를 대신하지 않는다.

## 근거와 한계

첫 조사의 시트 파싱과 프레임 재생 분석을 완료했다. 해당 코드·테스트·CI 연결을 확인했고 브라우저 실행은 하지 않았다. GPU 업로드·텍스처 메모리·다중 개체 프레임 시간·상태 전환은 미검증이다.

재사용 후보는 공통 프레임 재생 기준선이다. PNG와 WebP의 파일 크기 비교는 동일한 디코딩 결과·텍스처 크기·게임 부하 조건에서 별도로 해야 한다. [루트 라이선스](https://github.com/pixijs/pixijs/blob/5b41ee37fd36c61e089113345a8f12cf1c3323cf/LICENSE)를 확인했으며 외부 예제 자산의 사용 조건은 별도 확인 대상이다.

