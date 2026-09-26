# 기술 방향

## 서버

- 전투·보상·거래·적응 등 결과에 영향을 주는 계산은 서버가 처리한다.
- 접속 유지 여부에 따른 보상은 [게임 설계 > 접속과 미접속 보상](../game/design.md#접속과-미접속-보상)을 따른다.

## 적용 예정 기술

- [Redis](https://redis.io/docs/latest/)
- [Apache Kafka](https://kafka.apache.org/documentation/)
- [Apache Flink](https://flink.apache.org/what-is-flink/flink-architecture/)
- [Apache Airflow](https://airflow.apache.org/docs/apache-airflow/stable/index.html)
- [Prometheus](https://prometheus.io/docs/introduction/overview/)
- [Grafana](https://grafana.com/docs/grafana/latest/)

각 기술의 적용 범위·도입 순서·버전·배치·데이터 흐름은 구현 설계에서 정한다. 저장의 기준이 되는 데이터, 중복·지연 처리, 보존·복구 조건도 함께 정의한다.

## 에이전트 하네스

하네스는 에이전트가 문맥을 읽고, 도구를 실행하고, 결과를 관찰·검증하는 작업 환경이다. 하네스 개발에도 [작업 흐름](../workflow.md)을 적용한다.

### 역할

| 용어 | 역할 | 예 |
| --- | --- | --- |
| Guide | 작업 기준과 사용 방법 안내 | `AGENTS.md`, 명세, 도구 설명 |
| Sensor | 실행 상태와 결과 관찰 | 로그, 메트릭, 트레이스, 화면 |
| Verification | 명세·수용 기준 충족 여부 확인 | 테스트, 정적 검사, 시나리오 검증 |
| Gate | 판정 결과에 따른 다음 동작의 허용·차단 | 필수 CI 검사, 배포 조건 |
| Eval | 작업 사례 집합에 대한 기준별 성능 평가 | 성공률·정확성·시간·비용 비교 |

같은 도구가 여러 역할을 맡을 수 있다. 테스트는 Verification을 수행하고 결과를 Sensor로 제공할 수 있다. 그 결과가 실제 병합 조건에 연결되면 Gate로도 작동한다. Eval 결과 역시 기준을 정해 Gate에 연결할 수 있다.

### 명세 항목

- 대상 작업과 막아야 할 실패
- 제공할 문맥·도구·실행 권한
- 관찰 신호, 검사 기준, 결과 전달 경로
- 실행 환경의 격리·초기화·재현 방법
- Gate의 적용 위치와 실패·미실행 시 처리
- Eval의 사례·채점 기준·비교 조건·비용 측정

관찰·검증·차단의 적용 여부는 실제 코드와 설정으로 확인한다.
