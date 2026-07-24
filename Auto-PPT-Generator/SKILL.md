---
name: Auto-PPT-Generator
description: >
  콘텐츠만 주면 일관된 디자인의 PowerPoint(.pptx) 덱을 자동 생성하는 범용 프레젠테이션
  스킬. python-pptx로 표지·목차·핵심요약·KPI·불릿·비교·표·편집가능 차트·타임라인·프로세스·
  인용·이미지·마무리 등 14종 슬라이드를 고정 레이아웃으로 그려 텍스트 겹침·잘림 없이
  렌더링하고 한글 폰트도 안전하게 처리한다. 업무·실적·월간/분기 보고, 사업계획, 제안서,
  IR/피치덱, 회의 발표자료, 교육·강의 자료까지 무엇이든 발표용 슬라이드로 만들 때 사용.
  "PPT·파워포인트·발표자료·슬라이드·덱 만들어줘", "이 내용/데이터를 슬라이드로 정리해줘"처럼
  프레젠테이션 생성을 요청하면 트리거된다. 트리거되면 곧바로 파일을 만들지 말고 주제·테마·
  대략 구성/장수를 사용자에게 한 번 더 확인받은 뒤 생성할 것. (기존 .pptx 파일 편집, 슬라이드
  없는 단일 차트 이미지, 워드/엑셀/PDF 문서 생성은 이 스킬 대상이 아니다.)
---

# Auto-PPT-Generator

임의의 내용을 **콘텐츠 JSON → .pptx**로 변환하는 범용 프레젠테이션 생성기. 디자인
(레이아웃·컬러·폰트)은 테마로 고정돼 있고, 당신이 채우는 것은 콘텐츠 JSON뿐이다.

## 왜 이렇게 동작하나 (핵심 원리)

- **고정 영역 방식**: 모든 요소가 인치 단위의 정해진 박스 안에 놓이고 텍스트는 그 안에서
  word-wrap 된다. `references/slide_types.md`의 글자수 가이드만 지키면 레이아웃이 깨지지
  않는다 — 겹침·잘림이 구조적으로 방지된다.
- **역할 분리**: AI(당신)는 **콘텐츠 JSON**만 만들고, `engine.py`가 그 JSON을 슬라이드로
  조립한다. 슬라이드 좌표를 직접 계산하지 말 것 — 빌더가 알아서 배치한다.
- **네이티브 차트**: 차트는 이미지가 아니라 PowerPoint에서 더블클릭해 편집 가능한 실제
  차트로 삽입된다. 표도 실제 표 객체다. 사용자가 배포 후 수정할 수 있다.
- **한글 안전**: 폰트(기본 `Malgun Gothic`)를 Latin/한글/기호 모두에 적용해 글자가
  기본 폰트로 튀지 않는다.

## 워크플로

1. **무엇을 만들지 파악**한다. 사용자가 데이터/원문을 줬으면 그걸 쓰고, 주제만 줬으면
   보고 흐름을 스스로 설계한다(표지 → 목차 → 섹션별 본문 → 마무리).
2. **생성 직전 확인.** 파일을 바로 만들지 말고, 계획을 한 문단으로 요약해 사용자에게
   확인받는다 — 주제/제목, 테마(corporate·dark·minimal), 대략적인 슬라이드 구성과 장수,
   대상 청중·용도. 사용자가 "그냥 만들어"처럼 확인을 생략하라고 하면 바로 진행해도 된다.
3. **`references/slide_types.md`를 읽는다.** 각 슬라이드 타입이 요구하는 key와 글자수
   가이드가 전부 여기 있다. 콘텐츠를 만들기 전에 반드시 확인할 것.
4. **콘텐츠 JSON을 작성**한다. `assets/report_template.json`(업무 보고)이나
   `assets/pitch_template.json`(피치/제안)을 참고 골격으로 복사해 편집하면 빠르다.
5. **덱을 생성**한다:
   ```bash
   cd scripts
   python engine.py <content.json> <output/deck.pptx>
   ```
   출력 폴더는 자동 생성된다. 알 수 없는 타입이나 슬라이드 오류가 있으면 해당 슬라이드에
   에러 표식을 남기고 나머지는 정상 생성하며, 경고를 stdout에 출력한다.
6. **가능하면 렌더링해 눈으로 확인**한다(아래 "미리보기").

## 콘텐츠 JSON 구조

최상위는 `config`(선택) + `slides`(필수) 객체이거나, 그냥 슬라이드 리스트다.

```json
{
  "config": {"theme": "corporate", "font": "Malgun Gothic", "footer": "ACME · 대외비"},
  "slides": [
    {"type": "cover", "title": "2026 상반기 실적 리뷰", "subtitle": "...", "meta": ["전략팀", "2026-07-23"]},
    {"type": "kpi", "title": "핵심 지표", "tiles": [{"label": "매출", "value": "₩842억", "delta": "+8.4%", "trend": "up"}]},
    {"type": "chart", "title": "분기 매출", "chart_type": "bar", "categories": ["1Q","2Q"], "series": [{"name":"매출","values":[360,388]}]}
  ]
}
```

## 슬라이드 타입 (14종)

| type | 용도 | 대표 key |
|------|------|---------|
| `cover` | 표지 | title, subtitle, eyebrow, meta[] |
| `section` | 섹션 구분 | number, title, subtitle |
| `agenda` | 목차 | items[{title,desc}] |
| `summary` | 핵심 요약(카드) | lead, points[{title,desc}] |
| `kpi` | 지표 타일 | tiles[{label,value,delta,trend}] |
| `bullets` | 일반 본문 | lead, bullets[{text,sub}] |
| `two_col` | 2열 비교 | left/right{heading,items[]} |
| `table` | 데이터 표 | columns[], rows[[]], col_widths |
| `chart` | 차트 | chart_type, categories, series[], insight |
| `timeline` | 로드맵 | milestones[{label,title,desc}] |
| `process` | 프로세스 플로우 | steps[{title,desc}] |
| `quote` | 인용/한마디 | quote, author, role |
| `image` | 이미지+텍스트 | image, layout, body, caption |
| `closing` | 마무리/연락처 | title, message, contacts[] |

각 타입의 전체 key와 글자수 가이드는 **`references/slide_types.md`** 참조.

## 테마

`config.theme`: `corporate`(기본, 네이비+틸의 비즈니스 톤) · `dark`(다크 배경) ·
`minimal`(무채색+골드 포인트). 보고서엔 corporate, 사내 대시보드 느낌엔 dark,
미니멀/브랜드 중립엔 minimal을 권한다.

## 미리보기 (선택, Windows + PowerPoint)

PowerPoint가 설치돼 있으면 슬라이드를 PNG로 내보내 육안 검수할 수 있다:
```python
import win32com.client, os
app = win32com.client.Dispatch("PowerPoint.Application")
pres = app.Presentations.Open(os.path.abspath("output/deck.pptx"), WithWindow=False)
pres.Export(os.path.abspath("output/preview"), "PNG")
pres.Close(); app.Quit()
```
(LibreOffice가 있으면 `soffice --headless --convert-to pdf` 로도 검수 가능.)

## 새 슬라이드 타입 추가

1. `scripts/builders.py`에 `def build_xxx(slide, d, ctx): ...` 작성. 좌표는 상단의
   `MX`/`CW`/`BODY_TOP` 그리드와 `deck_kit` 헬퍼(`text/rect/table/chart/picture`)를 쓴다.
2. 파일 하단 `REGISTRY`에 `"xxx": build_xxx` 등록. 전면 배경 타입이면 `NO_FOOTER`에도 추가.
3. `references/slide_types.md`에 key·글자수 가이드를 추가.

## 주의

- 슬라이드당 정보 밀도를 지킬 것. 불릿 6개·표 7행·프로세스 5단계를 넘으면 두 장으로 쪼갠다.
- 색상 hex는 `#` 없이 6자리로 준다(예: `2E8B8B`).
- 이미지 경로가 없거나 잘못되면 크래시하지 않고 자리표시자를 그린다 — 배포 전 경로 확인.
- 값(KPI value)이 아주 길면 자동 축소되지만, 그래도 핵심 숫자는 짧게 유지하는 게 좋다.

## 의존성

`python-pptx` 필요: `pip install python-pptx`. (미리보기 PNG는 `pywin32` + PowerPoint.)
