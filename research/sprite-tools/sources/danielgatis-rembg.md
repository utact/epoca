# rembg 분석

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
  "repository": "https://github.com/danielgatis/rembg",
  "revision": "202e42649a8492a7c49f808de36608a7d1cbbfe3",
  "license": "MIT",
  "stars": 24945,
  "last_commit_at": "2026-09-20T17:13:21Z",
  "archived": false,
  "unknowns": {},
  "evidence_level": "code-inspected",
  "evidence": [
    "https://api.github.com/repos/danielgatis/rembg",
    "https://api.github.com/repos/danielgatis/rembg/commits/202e42649a8492a7c49f808de36608a7d1cbbfe3",
    "https://github.com/danielgatis/rembg/blob/202e42649a8492a7c49f808de36608a7d1cbbfe3/README.md",
    "https://github.com/danielgatis/rembg/blob/202e42649a8492a7c49f808de36608a7d1cbbfe3/LICENSE.txt",
    "https://github.com/danielgatis/rembg/blob/202e42649a8492a7c49f808de36608a7d1cbbfe3/rembg/bg.py",
    "https://github.com/danielgatis/rembg/blob/202e42649a8492a7c49f808de36608a7d1cbbfe3/tests/test_remove.py",
    "https://github.com/danielgatis/rembg/blob/202e42649a8492a7c49f808de36608a7d1cbbfe3/.github/workflows/lint_python.yml"
  ]
}
```

## 목적과 사용자

이미지의 배경을 제거하는 라이브러리·CLI다. 생성된 프레임의 전경 분리에도 사용할 수 있지만 애니메이션 생성이나 동일 개체 판정은 담당하지 않는다. [README](https://github.com/danielgatis/rembg/blob/202e42649a8492a7c49f808de36608a7d1cbbfe3/README.md)에서 사용 방식을 확인했다.

## 핵심 기능

입력 자료형 변환·마스크 추론·가장자리 처리·배경 합성을 분리한다. `only_mask`·색 오염 제거·알파 매팅·ViTMatte를 선택할 수 있고 세션 재사용이 가능하다. [remove 구현](https://github.com/danielgatis/rembg/blob/202e42649a8492a7c49f808de36608a7d1cbbfe3/rembg/bg.py)에서 분기와 반환을 확인했다.

바이트 출력은 PNG로 저장한다. 이 경로는 프레임별 배경 제거이며 시간축 일관성을 검사하지 않는다. 세션을 주지 않으면 읽은 버전에서는 `bria-rmbg`를 선택하므로 실험에서 모델 이름을 명시해야 한다.

## 실행 흐름

이미지를 읽고 방향을 보정한 뒤 세션의 `predict`로 마스크를 얻는다. 마스크와 선택한 가장자리 처리로 컷아웃을 만들고 입력 자료형에 맞춰 반환한다. 알파 매팅의 `ValueError`에서는 색 오염 제거 또는 알파 적용으로 대체한다. 모든 예외를 같은 방식으로 복구하는 것은 아니다. [처리·대체 경로](https://github.com/danielgatis/rembg/blob/202e42649a8492a7c49f808de36608a7d1cbbfe3/rembg/bg.py)에서 확인했다.

설치에는 선택한 CPU·GPU 추론 의존성과 모델 파일이 필요하다. 모델 다운로드와 실행은 하지 않았다. 코드의 라이선스만으로 모델의 사용 조건을 확정하지 않는다.

## 하네스 구성

아래 표는 추론·대체 처리·회귀 검사·개발 검사 순서다.

| 구성 요소와 연결 | 역할 | 판정 주체와 기준 | 상태와 다음 행동 | 근거 |
| --- | --- | --- | --- | --- |
| 이미지 → 마스크 → 컷아웃 | Transformer | 모델의 마스크 예측과 코드의 이미지 변환 | 결과 반환·화질 합격 판정은 별도 | [remove](https://github.com/danielgatis/rembg/blob/202e42649a8492a7c49f808de36608a7d1cbbfe3/rembg/bg.py) |
| 알파 매팅 예외 → 대체 처리 | Transformer | 코드의 예외 분기 | 특정 오류에서 대체 컷아웃 반환 | [매팅 예외 처리](https://github.com/danielgatis/rembg/blob/202e42649a8492a7c49f808de36608a7d1cbbfe3/rembg/bg.py) |
| 고정 이미지 → 모델별 결과 비교 | Sensor | 코드의 지각 해시 일치 Verification | 불일치 산출물 보존과 assertion 실패 | [회귀 테스트](https://github.com/danielgatis/rembg/blob/202e42649a8492a7c49f808de36608a7d1cbbfe3/tests/test_remove.py) |
| 변경 코드 → 린트 | Sensor | 코드 정적 검사 Verification | 실패 시 워크플로 실패·읽은 워크플로에는 pytest 호출 부재 | [린트 워크플로](https://github.com/danielgatis/rembg/blob/202e42649a8492a7c49f808de36608a7d1cbbfe3/.github/workflows/lint_python.yml) |

회귀 테스트의 지각 해시는 해당 기준 이미지와의 차이를 검사한다. 털 끝의 알파 정확도나 프레임 간 깜빡임의 정답 점수로 사용할 수 없다. 예외 후 이미지가 반환되어도 요청한 매팅 방식이 수행됐다고 기록하면 안 된다.

## 근거와 한계

첫 조사의 마스크·컷아웃·대체 처리 분석을 완료했다. 처리 코드와 한 회귀 테스트의 비교 방식 및 린트 연결을 확인했다. 테스트 실행·마스크 정확도·시간축 안정성·처리 시간은 미검증이다.

재사용 후보는 공통 후처리의 배경 제거 단계다. 모델과 가장자리 처리 방식을 별도 변수로 고정하고 흰색·검은색·유색 배경에서 털과 반투명 경계를 평가해야 한다. [루트 라이선스](https://github.com/danielgatis/rembg/blob/202e42649a8492a7c49f808de36608a7d1cbbfe3/LICENSE.txt)를 확인했으며 모델별 라이선스·외부 서비스 조건·입력 권리는 이번 조사에서 검증하지 않았다.

