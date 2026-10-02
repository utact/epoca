# DragonBonesJS 분석

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
  "repository": "https://github.com/DragonBones/DragonBonesJS",
  "revision": "64b6c69ae35777c2404be68c9192e2c56906079e",
  "license": "MIT",
  "stars": 851,
  "last_commit_at": "2025-05-24T14:08:50Z",
  "archived": false,
  "unknowns": {},
  "evidence_level": "code-inspected",
  "evidence": [
    "https://api.github.com/repos/DragonBones/DragonBonesJS",
    "https://api.github.com/repos/DragonBones/DragonBonesJS/commits/64b6c69ae35777c2404be68c9192e2c56906079e",
    "https://github.com/DragonBones/DragonBonesJS/blob/64b6c69ae35777c2404be68c9192e2c56906079e/README.md",
    "https://github.com/DragonBones/DragonBonesJS/blob/64b6c69ae35777c2404be68c9192e2c56906079e/LICENSE",
    "https://github.com/DragonBones/DragonBonesJS/blob/64b6c69ae35777c2404be68c9192e2c56906079e/DragonBones/src/dragonBones/animation/Animation.ts",
    "https://github.com/DragonBones/DragonBonesJS/blob/64b6c69ae35777c2404be68c9192e2c56906079e/Pixi/8.x/src/dragonBones/pixi/PixiFactory.ts",
    "https://github.com/DragonBones/DragonBonesJS/blob/64b6c69ae35777c2404be68c9192e2c56906079e/Pixi/8.x/package.json"
  ]
}
```

## 목적과 사용자

제작된 뼈대·애니메이션 데이터를 게임 엔진에서 재생하는 JavaScript·TypeScript 런타임이다. 프레임 이미지 생성기나 리그 제작 편집기와 구분한다. [README](https://github.com/DragonBones/DragonBonesJS/blob/64b6c69ae35777c2404be68c9192e2c56906079e/README.md)에서 여러 엔진 어댑터와 외부 제작 도구 안내를 확인했다.

## 핵심 기능

애니메이션 이름으로 재생하고 반복 수·시작 위치·페이드 시간·레이어·그룹을 설정한다. [Animation 구현](https://github.com/DragonBones/DragonBonesJS/blob/64b6c69ae35777c2404be68c9192e2c56906079e/DragonBones/src/dragonBones/animation/Animation.ts)에서 `play`·`fadeIn`·`gotoAndPlayByTime`을 확인했다.

Pixi 어댑터는 캐시된 뼈대·텍스처 데이터로 표시 객체를 만들고 시계에 연결한다. [PixiFactory](https://github.com/DragonBones/DragonBonesJS/blob/64b6c69ae35777c2404be68c9192e2c56906079e/Pixi/8.x/src/dragonBones/pixi/PixiFactory.ts)에서 확인했다. 리그를 실행 중 계산하는 방식과 결과를 이미지 프레임으로 굽는 방식은 후속 개념 정의에서 별도 경로로 다뤄야 한다.

## 실행 흐름

제작 도구가 만든 데이터와 텍스처를 준비한 뒤 런타임의 팩토리로 뼈대 표시 객체를 만든다. 게임 루프의 시간 진행에 따라 애니메이션을 갱신한다. Pixi 8.x용 디렉터리와 TypeScript 빌드 명령은 [어댑터 패키지](https://github.com/DragonBones/DragonBonesJS/blob/64b6c69ae35777c2404be68c9192e2c56906079e/Pixi/8.x/package.json)에서 확인했다.

이 디렉터리가 있다는 사실만으로 최신 PixiJS 버전과의 호환성을 보장하지 않는다. 리그 제작 도구·자산의 취득과 실제 통합 빌드는 수행하지 않았다.

## 하네스 구성

아래 표는 데이터 연결·상태 재생·개발 확인 순서다.

| 구성 요소와 연결 | 역할 | 판정 주체와 기준 | 상태와 다음 행동 | 근거 |
| --- | --- | --- | --- | --- |
| 캐시된 데이터 → 표시 객체 | Transformer | 코드의 이름 조회와 객체 구성 | 해당 뼈대 부재 시 null 반환·호출자 처리 필요 | [buildArmatureDisplay](https://github.com/DragonBones/DragonBonesJS/blob/64b6c69ae35777c2404be68c9192e2c56906079e/Pixi/8.x/src/dragonBones/pixi/PixiFactory.ts) |
| 애니메이션 이름 → 재생 상태 | Transformer·Sensor | 코드의 애니메이션 존재 Verification | 없는 이름의 경고·null 반환 | [playConfig](https://github.com/DragonBones/DragonBonesJS/blob/64b6c69ae35777c2404be68c9192e2c56906079e/DragonBones/src/dragonBones/animation/Animation.ts) |
| 어댑터 소스 → 빌드 | 해당 범위의 개발 도구 | TypeScript 빌드 | 읽은 패키지에는 build·debug 명령·test 명령 부재 | [패키지 스크립트](https://github.com/DragonBones/DragonBonesJS/blob/64b6c69ae35777c2404be68c9192e2c56906079e/Pixi/8.x/package.json) |

일반 재생 라이브러리의 변환·오류 처리를 AI 생성 하네스로 확대 해석하지 않는다. 전역 테스트·원격 CI·병합 조건은 이 파일들만으로 판단하지 않는다.

## 근거와 한계

첫 조사의 리그 재생 경로 분석을 완료했다. 상태 전환과 표시 객체 연결은 코드로 확인했다. 변형 품질·관절 제약·스킨 교체·이미지 베이크·최신 엔진 호환성은 미검증이다.

재사용 후보는 리그 기반 경로의 런타임 대조군이다. 털 모양의 변경에 파츠나 메시 수정이 필요한지는 실제 자산으로 검증해야 한다. [런타임 라이선스](https://github.com/DragonBones/DragonBonesJS/blob/64b6c69ae35777c2404be68c9192e2c56906079e/LICENSE)가 외부 제작 도구와 예제 자산의 조건을 대신하지 않는다.

