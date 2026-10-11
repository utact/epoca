# 브랜드 에셋

사용자가 제공한 EPOCA 가로 로고와 심볼의 픽셀을 재생성하거나 확대·축소하지 않고 배치와 캔버스를 조정한 에셋이다.

## 파일과 용도

PNG는 편집 기준본으로 보관하고 웹 표시에는 같은 이름의 무손실 WebP를 사용한다. 각 PNG와 WebP의 크기·색상·알파 채널은 동일하다.

| 이름 | 용도 | 편집 기준본 | 웹 표시용 | 크기 | 캔버스 비율 |
| --- | --- | --- | --- | --- | --- |
| `epoca-symbol` | 심볼 | [PNG](epoca-symbol.png) | [WebP](epoca-symbol.webp) | 1440 × 1440 px | 1:1 |
| `epoca-wordmark` | 가로 로고 | [PNG](epoca-wordmark.png) | [WebP](epoca-wordmark.webp) | 2172 × 724 px | 3:1 |

## 배치 기준

외곽과 여백은 0–255 범위의 알파 값이 8 이상인 픽셀을 기준으로 측정한다. 거의 보이지 않는 픽셀도 원본대로 보존하므로 알파 값이 0보다 큰 모든 픽셀의 경계와는 차이가 있다.

- 가로 로고의 E–P·P–O·O–C·C–A 간격은 기존 E–P 간격인 79 px로 통일한다.
- 가로 로고의 바깥 여백은 왼쪽 270 px·오른쪽 271 px·위쪽 62 px·아래쪽 62 px다.
- 심볼의 바깥 여백은 왼쪽 175 px·오른쪽 176 px·위쪽 134 px·아래쪽 135 px다.
- 화면에 배치할 때 가로세로 비율을 유지한다. 용도별 최소 표시 크기와 실제 화면 배치는 별도로 확인한다.

## WebP 갱신

[WebP](https://developers.google.com/speed/webp)는 무손실 압축과 투명도를 지원한다. 현재 파일은 Pillow와 libwebp 1.4.0에서 `lossless=True`, `quality=100`, `method=6`, `exact=True`로 변환했다. 완전히 투명한 픽셀의 RGB도 보존하며 PNG를 수정하면 대응하는 WebP를 다시 변환하고 디코딩 후 전체 RGBA 픽셀의 일치를 확인한다.

저장소 루트에서 Python과 Pillow를 사용할 수 있는 환경이면 다음 명령으로 갱신한다. 무손실 모드의 `quality=100`은 이미지 품질을 낮추지 않고 압축에 들이는 노력을 지정한다.

```python
from pathlib import Path
from PIL import Image

for path in sorted(Path("assets/brand").glob("*.png")):
    with Image.open(path) as source:
        original = source.convert("RGBA")
    output = path.with_suffix(".webp")
    original.save(output, lossless=True, quality=100, method=6, exact=True)
    with Image.open(output) as decoded:
        assert decoded.size == original.size
        assert decoded.convert("RGBA").tobytes() == original.tobytes()
```
