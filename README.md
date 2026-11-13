# my-skills

직접 만든 Agent Skill 모음입니다. 특정 AI에 묶이지 않고 **여러 에이전트**(Codex, Claude Code 등
파일·명령 실행 도구가 있는 환경)를 염두에 두고 만들었으며, 대화창만 있는 AI에서도 같은 절차로 동작합니다.
각 스킬은 최상위 폴더 하나로 구성되며, 그 안의 `SKILL.md`가 스킬의 진입점입니다.

## 수록 스킬

인문·사회·경영 분야 강사를 위한 **교육자료 스킬 4종**입니다. 스크립트·해시·업체 템플릿에 의존하지 않고,
시작할 때 분야(도메인)를 한 번 질문해 내용을 맞춥니다.

| 스킬 | 설명 |
|------|------|
| [curriculum-to-lesson](curriculum-to-lesson) | 커리큘럼 확인(없으면 질의응답), 타임테이블·블록 설계, 블록별 자료 조사. 제작 지시문과 조사 결과를 Markdown으로 남깁니다. |
| [edu-create](edu-create) | 제작 지시문과 조사 결과를 읽어 교안(슬라이드)과 수강생용 실습·활동 자료를 신규 제작하고 자체 검증합니다. |
| [education-prep](education-prep) | 기존 교육자료를 분석해 차시별 진행안을 만들고, 강사 승인 후 수정해 배포 가능한 상태로 준비합니다. |
| [education-review](education-review) | 진행안·수정본을 독립적으로 검수합니다. 자료는 고치지 않고 문제·근거·수정 제안만 냅니다(읽기 전용). |

### 권장 흐름

```
curriculum-to-lesson → edu-create            (신규 제작)
기존 자료 → education-prep → education-review  (수정·배포 준비 → 검수)
```

## 설치

사용하는 에이전트의 스킬 디렉토리에 필요한 스킬 폴더를 복사하면 됩니다. 아래는 Claude Code 예시이며,
Codex 등 다른 에이전트는 해당 환경의 스킬 경로를 사용하세요. 각 스킬의 `agents/openai.yaml`에는 표시 이름과
기본 프롬프트가 들어 있습니다.

```bash
# macOS/Linux
cp -r curriculum-to-lesson edu-create education-prep education-review ~/.claude/skills/

# Windows (PowerShell)
Copy-Item -Recurse curriculum-to-lesson,edu-create,education-prep,education-review $HOME\.claude\skills\
```

## 라이선스

[MIT](LICENSE)
