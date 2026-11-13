# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 목적

이 저장소(`my-skills`)는 직접 만든 Agent Skill을 모아 GitHub에 배포하는 **모노레포**다.
최상위 폴더 하나가 스킬 하나이고, 그 안의 `SKILL.md`가 진입점이다.

현재 수록 스킬:
- **교육자료 스킬 4종** — 인문·사회·경영 강사용. 특정 AI에 묶이지 않고 Codex·Claude Code 같은
  에이전트 환경을 기본 대상으로 하되 대화 전용 AI에서도 동작한다. 스크립트·해시·업체 템플릿 의존 없음.
  모든 스킬은 시작 시 **분야(도메인)를 한 번 질문**해 채운다. 흐름은 아래 순서다.
  - **`curriculum-to-lesson/`** — 커리큘럼 확인(없으면 질의응답), 타임테이블·블록 설계, 블록별 자료 조사.
    `설계/00_제작지시문.md`와 `설계/조사/B01_*.md`를 만든다.
  - **`edu-create/`** — 위 두 산출물을 읽어 교안과 수강생 자료를 신규 제작하고 자체 검증한다.
  - **`education-prep/`** — 기존 자료의 분석·진행안·승인 후 수정·배포 목록 준비.
  - **`education-review/`** — 진행안·수정본 독립 검수(읽기 전용, 별도 세션).
  `education-prep`과 `education-review`의 `references/standards.md`는 **동일 사본**이므로
  한쪽을 고치면 다른 쪽도 같이 고친다.

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
