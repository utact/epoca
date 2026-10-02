# Sprute 분석

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
  "repository": "https://github.com/sprited-ai/sprute",
  "revision": "627ba7c1121ac2ee8355c844197c20d1eef38119",
  "license": "MIT",
  "stars": 2,
  "last_commit_at": "2026-09-30T05:59:56Z",
  "archived": false,
  "unknowns": {},
  "evidence_level": "code-inspected",
  "evidence": [
    "https://api.github.com/repos/sprited-ai/sprute",
    "https://api.github.com/repos/sprited-ai/sprute/commits/627ba7c1121ac2ee8355c844197c20d1eef38119",
    "https://github.com/sprited-ai/sprute/blob/627ba7c1121ac2ee8355c844197c20d1eef38119/README.md",
    "https://github.com/sprited-ai/sprute/blob/627ba7c1121ac2ee8355c844197c20d1eef38119/LICENSE",
    "https://github.com/sprited-ai/sprute/blob/627ba7c1121ac2ee8355c844197c20d1eef38119/src/sprute/animate.py",
    "https://github.com/sprited-ai/sprute/blob/627ba7c1121ac2ee8355c844197c20d1eef38119/src/sprute/comfy.py",
    "https://github.com/sprited-ai/sprute/blob/627ba7c1121ac2ee8355c844197c20d1eef38119/src/sprute/motion.py",
    "https://github.com/sprited-ai/sprute/blob/627ba7c1121ac2ee8355c844197c20d1eef38119/src/sprute/models.py",
    "https://github.com/sprited-ai/sprute/blob/627ba7c1121ac2ee8355c844197c20d1eef38119/workflows/sprute-animate-character.api.json",
    "https://github.com/sprited-ai/sprute/blob/627ba7c1121ac2ee8355c844197c20d1eef38119/pyproject.toml"
  ]
}
```

## 목적과 사용자

텍스트나 참조 이미지에서 여러 방향의 캐릭터와 애니메이션을 만드는 로컬 GPU용 CLI다. 범용 시트 생성과 달리 템플릿·구동 모션·ComfyUI 워크플로를 연결한다. [README](https://github.com/sprited-ai/sprute/blob/627ba7c1121ac2ee8355c844197c20d1eef38119/README.md)에서 지원 경로를 확인했다.

## 핵심 기능

기준 캐릭터·8방향 이미지·대기·걷기·달리기 애니메이션을 단계별로 생성한다. 동작 입력은 GLB 리그 모션 또는 사용자가 준비한 투명 WebP 영상이다. 후자는 방향 이미지와 같은 크기를 요구한다. [모션 처리](https://github.com/sprited-ai/sprute/blob/627ba7c1121ac2ee8355c844197c20d1eef38119/src/sprute/motion.py)에서 선택·검사를 확인했다.

[애니메이션 워크플로](https://github.com/sprited-ai/sprute/blob/627ba7c1121ac2ee8355c844197c20d1eef38119/workflows/sprute-animate-character.api.json)에는 SCAIL-2 계열 모델·LoRA·BiRefNet 배경 제거·무손실 animated WebP 저장 노드가 연결돼 있다. 이는 읽은 경로의 설정이며 실제 생성에 사용한 모델이라는 뜻은 아니다. [모델 목록](https://github.com/sprited-ai/sprute/blob/627ba7c1121ac2ee8355c844197c20d1eef38119/src/sprute/models.py)은 다운로드 파일과 고정 리비전을 기록한다.

## 실행 흐름

방향 이미지와 모션을 읽고 GLB이면 먼저 구동 영상을 렌더링한다. 입력 이미지·영상은 내용 해시 기반 이름으로 워크플로에 전달한다. 저장된 워크플로와 현재 그래프가 같으면 기존 출력 파일을 반환하고 그 외에는 ComfyUI를 실행한다. [animate](https://github.com/sprited-ai/sprute/blob/627ba7c1121ac2ee8355c844197c20d1eef38119/src/sprute/animate.py)와 [실행 연결](https://github.com/sprited-ai/sprute/blob/627ba7c1121ac2ee8355c844197c20d1eef38119/src/sprute/comfy.py)에서 확인했다.

Python과 GPU 추론 환경이 필요하다. 설치 선언은 [패키지 설정](https://github.com/sprited-ai/sprute/blob/627ba7c1121ac2ee8355c844197c20d1eef38119/pyproject.toml)에서 확인했다. 모델 다운로드 크기·라이선스·가용 VRAM·실제 처리 시간은 실행 준비 단계에서 확인해야 한다. 워크플로 일치에 따른 캐시 재사용은 출력 품질의 검증이나 모델 파일 변경까지 포함한 재현성 보장이 아니다.

## 하네스 구성

아래 표는 입력 검사·생성·출력 보존 순서다.

| 구성 요소와 연결 | 역할 | 판정 주체와 기준 | 상태와 다음 행동 | 근거 |
| --- | --- | --- | --- | --- |
| 구동 영상 → 생성 입력 | Gate | 코드의 크기·최소 5프레임·첫 프레임 투명 픽셀 Verification | 위반 시 예외·사용자 입력 수정 | [check_driving_video](https://github.com/sprited-ai/sprute/blob/627ba7c1121ac2ee8355c844197c20d1eef38119/src/sprute/motion.py) |
| 입력·그래프 → ComfyUI 출력 | Transformer·Sensor | 모델 생성과 코드의 프로세스·JSON·파일 검사 | 실패 코드·결과 누락 시 예외·자동 재생성 루프 미확인 | [run_workflow](https://github.com/sprited-ai/sprute/blob/627ba7c1121ac2ee8355c844197c20d1eef38119/src/sprute/comfy.py) |
| 완료 바이트 → 최종 파일 | Transformer | 코드의 임시 파일 저장·교체 | 성공 시 파일 교체·완료 이벤트 전달 | [출력 저장](https://github.com/sprited-ai/sprute/blob/627ba7c1121ac2ee8355c844197c20d1eef38119/src/sprute/animate.py) |

입력 검사는 첫 프레임의 투명 픽셀 존재만 확인하므로 전체 시퀀스의 알파 품질을 보장하지 않는다. 모델의 4n+1 프레임 제약으로 끝부분이 잘릴 수 있다는 문서·주석이 있어 재생 시간과 종료 자세 보존을 확인해야 한다.

[고정 커밋의 전체 트리](https://api.github.com/repos/sprited-ai/sprute/git/trees/627ba7c1121ac2ee8355c844197c20d1eef38119?recursive=1)에서 테스트 경로와 GitHub Actions 워크플로를 찾지 못했다. 다른 저장소나 외부 CI의 검사 존재 여부는 미확인이다. 프로세스 성공과 동작 품질 합격을 구분한다.

## 근거와 한계

첫 조사의 템플릿 기반 생성 경로와 입력·실행 검사를 분석했다. 실제 생성·품질 Eval·프레임 시간 보존·사족보행 적용은 미검증이다. 제공된 마네킹과 구동 모션이 늑대 등 다른 신체 구조에 적합하다고 가정하지 않는다.

재사용 후보는 명시적인 구동 모션을 둔 생성 대조군과 입력 해시·워크플로 기록 방식이다. [코드 라이선스](https://github.com/sprited-ai/sprute/blob/627ba7c1121ac2ee8355c844197c20d1eef38119/LICENSE)가 모델·LoRA·참조 이미지·동작 자산의 조건을 대신하지 않는다. 해당 조건 확인 전에는 상용 배포 가능한 구성으로 확정하지 않는다.

