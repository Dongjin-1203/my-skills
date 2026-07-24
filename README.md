# my-skills

개인적으로 만든 [Claude Agent Skills](https://docs.claude.com/en/docs/claude-code/skills) 모음입니다.
각 스킬은 최상위 폴더 하나로 구성되며, 그 안의 `SKILL.md`가 스킬의 진입점입니다.

## 수록 스킬

| 스킬 | 설명 |
|------|------|
| [Auto-PPT-Generator](Auto-PPT-Generator) | 콘텐츠 JSON으로 일관된 디자인의 범용 PowerPoint(.pptx) 덱을 자동 생성. 업무·실적 보고, 제안서, 피치덱, 교육 자료 등 14종 슬라이드 지원. |

## 설치

개별 스킬 폴더를 Claude Code 스킬 디렉토리에 복사하면 됩니다.

```bash
# 예: Auto-PPT-Generator 설치 (macOS/Linux)
cp -r Auto-PPT-Generator ~/.claude/skills/

# Windows (PowerShell)
Copy-Item -Recurse Auto-PPT-Generator $HOME\.claude\skills\
```

스킬별 의존성은 각 폴더의 `requirements.txt`를 참고하세요.
(예: Auto-PPT-Generator는 `pip install python-pptx` 필요)

## 라이선스

[MIT](LICENSE)
