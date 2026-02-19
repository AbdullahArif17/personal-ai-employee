---
id: 1
title: Create Personal AI Employee Constitution
stage: constitution
date: 2026-02-20
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: default-user
command: /sp.constitution
labels: [constitution, governance, principles]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
---

## Prompt

Create governing principles for a Personal AI Employee project:

1. LOCAL-FIRST: All sensitive data stays on local machine. Obsidian vault is the single source of truth.
2. SECURITY: All credentials in .env file only. Never stored in vault or committed to git.
3. HUMAN-IN-THE-LOOP: No external action (email send, payment, social post) executes without a human moving a file to /Approved.
4. AGENT SKILLS: All AI logic must be implemented as SKILL.md files that Claude Code can read and follow.
5. DRY-RUN DEFAULT: All watcher and action scripts default to DRY_RUN=true during development.
6. PYTHON 3.13+: All scripts use Python 3.13 or higher with uv for package management.
7. FAIL SAFE: On any error, scripts log and pause — they never silently skip or auto-retry destructive actions.
8. AUDITABILITY: Every action the AI takes is logged to /Vault/Logs/YYYY-MM-DD.json.

## Response snapshot

Created a comprehensive constitution file for the Personal AI Employee project with 8 core principles covering local-first data handling, security, human oversight, agent skills, development standards, and fail-safes. The constitution establishes governance for the project with sections on technology stack, security requirements, data management, and development workflow.

## Outcome

- ✅ Impact: Created foundational governance document establishing project principles
- 🧪 Tests: No tests required for constitution creation
- 📁 Files: Updated .specify/memory/constitution.md with project-specific principles
- 🔁 Next prompts: Ready for implementation of specific features following these principles
- 🧠 Reflection: Constitution provides clear guidance for future development decisions

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin implementing specific AI employee features following these principles