# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 목적

이 저장소(`my-skills`)는 직접 만든 Agent Skill을 모아 GitHub에 배포하는 **모노레포**다.
최상위 폴더 하나가 스킬 하나이고, 그 안의 `SKILL.md`가 진입점이다.

현재 수록 스킬:
- **`Auto-PPT-Generator/`** — 콘텐츠 JSON → PowerPoint(.pptx) 범용 덱 생성기.
  `scripts/engine.py`가 JSON을 받아 `builders.py`의 14종 슬라이드 빌더로 조립하고,
  좌표·색·폰트 등 저수준 그리기는 전부 `deck_kit.py`에 모여 있다. 새 슬라이드 타입은
  빌더 함수 추가 + `REGISTRY` 등록 + `references/slide_types.md` 문서화의 3단계로 넣는다.

새 스킬을 추가할 때는 최상위에 폴더를 만들고 같은 구조(`SKILL.md` + 필요시
`scripts/`·`references/`·`assets/`)를 따른다.

## 개발 환경

- **OS/셸**: Windows 11. 두 가지 셸을 쓸 수 있고 문법이 *서로 다르다*:
  - PowerShell 도구 (기본) — Windows PowerShell 5.1. `&&`/`||` 체이닝 불가, 삼항 연산자 없음.
  - Bash 도구 — Git Bash (POSIX). Unix 스타일 스크립트에 사용.
  호출하는 셸에 맞는 문법을 쓰고, 문법을 섞지 말 것.
- **GitHub**: `gh` CLI가 설치·인증되어 있음. GitHub 작업은 raw git 원격 조작보다
  `gh repo create`, `gh pr` 등을 우선 사용.
- 커밋 / 푸시는 명시적으로 요청받았을 때만 수행한다. 저장소를 새로 시작할 때는 기본 브랜치에서
  바로 작업한다고 가정하지 말고, 저장소를 만들고 브랜치에서 커밋할 것.

## 빌드 / 검증 (Auto-PPT-Generator)

```bash
pip install python-pptx           # 의존성
cd Auto-PPT-Generator/scripts
python engine.py ../assets/report_template.json ../output/demo.pptx
```
엔진은 출력 폴더를 자동 생성하고, 슬라이드 하나가 실패해도 그 슬라이드에만 에러 표식을
남긴 뒤 나머지를 계속 생성하며 경고를 stdout에 출력한다. 즉 **"OK ->" 뒤에 경고가 없어야
정상**이다.

레이아웃 변경은 눈으로 확인하는 게 가장 확실하다. PowerPoint가 설치된 Windows에서는
`pywin32`로 슬라이드를 PNG로 내보내 검수할 수 있다 (경로는 반드시 절대경로):
```python
import win32com.client, os
app = win32com.client.Dispatch("PowerPoint.Application")
pres = app.Presentations.Open(os.path.abspath("../output/demo.pptx"), WithWindow=False)
pres.Export(os.path.abspath("../output/preview"), "PNG")
pres.Close(); app.Quit()
```

## 스킬 구조 규약

모든 Agent Skill은 YAML frontmatter가 있는 `SKILL.md`를 포함하는 디렉토리다:

```yaml
---
name: my-skill-name          # kebab-case, 디렉토리 이름과 일치
description: 무엇을 하는지(WHAT)와 언제 쓰는지(WHEN)를 한 줄로 기술 — Claude가 이 스킬을
  불러올지 판단하는 유일한 신호이므로 트리거를 명확하게 담을 것.
---
```

frontmatter 아래에는 Markdown 본문(스킬이 실제로 수행하는 지침/워크플로)이 온다.
보조 파일(스크립트, 레퍼런스, fixture)은 `SKILL.md`와 같은 디렉토리에 두고 상대 경로로 참조한다.

여기 적용되는 설계 지침:
- `description`은 문서가 아니라 **탐색용 훅**이다 — 스킬을 트리거해야 할 문구와 의도를 최대한 담을 것.
  일단 배포한 뒤에는 name을 바꾸지 말 것.
- 스킬 본문은 자기완결적으로 유지하고, 이 디렉토리의 주변 상태에 의존하지 말 것.

## 작성 워크플로

- 새 스킬은 보일러플레이트를 직접 짜기보다 이 세션에서 사용 가능한 **`skill-creator`** 스킬로
  스캐폴딩하고 다듬을 것.
- 스킬을 GitHub에 배포하기 전에 저장소 이름, 공개 여부(public/private), 그리고 새 저장소인지
  기존 저장소에 추가하는지를 확인할 것 — 되돌리기 어렵고 외부에 노출되는 작업이므로 반드시 물어볼 것.
