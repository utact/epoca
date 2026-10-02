# free-tex-packer-core 분석

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
  "repository": "https://github.com/odrick/free-tex-packer-core",
  "revision": "f918f61569e669df61825ec1040540f1d8470acb",
  "license": "MIT",
  "stars": 151,
  "last_commit_at": "2026-07-24T08:42:45Z",
  "archived": false,
  "unknowns": {},
  "evidence_level": "code-inspected",
  "evidence": [
    "https://api.github.com/repos/odrick/free-tex-packer-core",
    "https://api.github.com/repos/odrick/free-tex-packer-core/commits/f918f61569e669df61825ec1040540f1d8470acb",
    "https://github.com/odrick/free-tex-packer-core/blob/f918f61569e669df61825ec1040540f1d8470acb/README.md",
    "https://github.com/odrick/free-tex-packer-core/blob/f918f61569e669df61825ec1040540f1d8470acb/LICENSE.md",
    "https://github.com/odrick/free-tex-packer-core/blob/f918f61569e669df61825ec1040540f1d8470acb/index.js",
    "https://github.com/odrick/free-tex-packer-core/blob/f918f61569e669df61825ec1040540f1d8470acb/PackProcessor.js",
    "https://github.com/odrick/free-tex-packer-core/blob/f918f61569e669df61825ec1040540f1d8470acb/utils/imageFormats.js",
    "https://github.com/odrick/free-tex-packer-core/blob/f918f61569e669df61825ec1040540f1d8470acb/package.json",
    "https://github.com/odrick/free-tex-packer-core/blob/f918f61569e669df61825ec1040540f1d8470acb/tests/rotation.test.js"
  ]
}
```

## 목적과 사용자

여러 이미지를 텍스처 아틀라스로 배치하고 엔진용 메타정보를 만드는 Node.js 라이브러리다. 프레임의 그림이나 동작을 생성하는 도구가 아니다. [README](https://github.com/odrick/free-tex-packer-core/blob/f918f61569e669df61825ec1040540f1d8470acb/README.md)에서 입출력과 옵션을 확인했다.

## 핵심 기능

트리밍·회전·동일 입력 감지·여백·테두리 확장·다중 시트와 여러 내보내기 형식을 지원한다. 원본 크기 `sourceSize`와 잘린 영역 `spriteSourceSize`를 프레임 사각형과 구분해 보존한다. [패킹 구현](https://github.com/odrick/free-tex-packer-core/blob/f918f61569e669df61825ec1040540f1d8470acb/PackProcessor.js)에서 확인했다.

PNG·JPEG·WebP 출력 경로가 있다. 읽은 버전의 WebP 인코딩은 `quality: 90`을 지정하며 무손실 옵션을 지정하지 않는다. 단순 포맷 교체를 무손실 비교로 기록할 수 없다. [포맷 처리](https://github.com/odrick/free-tex-packer-core/blob/f918f61569e669df61825ec1040540f1d8470acb/utils/imageFormats.js)에서 확인했다.

## 실행 흐름

이미지의 경로와 바이트 목록을 받아 디코딩하고 옵션을 정규화한다. 패킹 후 렌더링·메타정보 출력으로 파일 이름과 버퍼를 반환한다. 호출자는 반환 파일의 저장을 담당한다. [API 진입점](https://github.com/odrick/free-tex-packer-core/blob/f918f61569e669df61825ec1040540f1d8470acb/index.js)과 [패키지 의존성](https://github.com/odrick/free-tex-packer-core/blob/f918f61569e669df61825ec1040540f1d8470acb/package.json)을 확인했다.

`loadImage`는 읽기 실패를 콘솔에 출력하고 예외를 다시 던지지 않는다. 따라서 완료 반환만으로 모든 입력 프레임이 포함됐다고 판단하지 않고 입력 이름과 출력 이름의 대응을 확인해야 한다. 실제 실패 입력 실행은 아직 하지 않았다.

## 하네스 구성

아래 표는 입력·패킹·회귀 검사 순서다.

| 구성 요소와 연결 | 역할 | 판정 주체와 기준 | 상태와 다음 행동 | 근거 |
| --- | --- | --- | --- | --- |
| 입력 버퍼 → 디코딩 목록 | Transformer·Sensor | 코드의 디코딩 성공 여부 | 읽기 실패 시 로그 후 해당 이미지 누락 가능·완전성 별도 검사 필요 | [loadImage](https://github.com/odrick/free-tex-packer-core/blob/f918f61569e669df61825ec1040540f1d8470acb/index.js) |
| 이미지 사각형 → 아틀라스 배치 | Transformer·Gate | 코드의 최소 크기와 패킹 조건 Verification | 크기 위반 시 오류 콜백·호출자가 옵션 수정 | [pack](https://github.com/odrick/free-tex-packer-core/blob/f918f61569e669df61825ec1040540f1d8470acb/PackProcessor.js) |
| 방향별 픽셀 → 회전 검증 | Sensor | 코드의 좌표·색상 일치 Verification | assertion 실패로 검사 종료 | [회전 회귀 테스트](https://github.com/odrick/free-tex-packer-core/blob/f918f61569e669df61825ec1040540f1d8470acb/tests/rotation.test.js) |

`npm test`는 Node의 테스트 러너를 호출한다. [테스트 명령](https://github.com/odrick/free-tex-packer-core/blob/f918f61569e669df61825ec1040540f1d8470acb/package.json)을 확인했지만 실행 결과나 원격 필수 검사는 확인하지 않았다. 패킹 효율은 이미지 의미나 애니메이션 품질의 점수가 아니다.

## 근거와 한계

첫 조사의 패킹·메타정보·포맷 처리 분석을 완료했다. 입력 오류 처리와 회전 테스트도 코드로 확인했다. 프레임 누락·트리밍 복원·실제 엔진 호환성·메모리·속도는 실행 검증이 필요하다.

재사용 후보는 생성 방식에 공통인 아틀라스 출력 단계다. 입력 순서·재생 시간은 패킹 위치와 별도로 보존해야 한다. [루트 라이선스](https://github.com/odrick/free-tex-packer-core/blob/f918f61569e669df61825ec1040540f1d8470acb/LICENSE.md)를 확인했다. 외부 압축 서비스는 선택 옵션이며 기본 실험에 자동 포함하지 않는다.

