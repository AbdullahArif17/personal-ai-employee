---
id: 1
title: Create Bronze Tier Personal AI Employee Spec
stage: spec
date: 2026-02-20
surface: agent
model: claude-sonnet-4-5-20250929
feature: ai_employee
branch: master
user: default-user
command: /sp.specify
labels: [specification, ai-employee, bronze-tier]
links:
  spec: specs/ai_employee/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/ai_employee/spec.md
tests:
---

## Prompt

Build a Bronze-tier Personal AI Employee using Claude Code and Obsidian.

WHAT IT DOES:
A local automation system where Claude Code acts as an AI employee that monitors
an Obsidian markdown vault, processes incoming tasks, and writes structured outputs —
all running on the user's local machine.

CORE FEATURES:
1. Obsidian Vault Structure: Create AI_Employee_Vault with folders /Inbox, /Needs_Action, /Done, /Logs, /Pending_Approval, /Approved
2. Dashboard.md: A live summary file showing pending items, recent activity, and status
3. Company_Handbook.md: Rules of engagement for the AI (tone, approval thresholds, contact list)
4. Filesystem Watcher: A Python script that monitors /Inbox. When a new file appears, it copies it to /Needs_Action with a metadata .md sidecar file
5. Agent SKILL.md files: Markdown skill files Claude Code reads to know HOW to process tasks (e.g., how to triage an inbox item, how to update the dashboard)
6. Claude Code Integration: Claude Code reads /Needs_Action, processes each item following the SKILL.md instructions, writes a plan or response, updates Dashboard.md, and moves the item to /Done

WHAT IT DOES NOT DO (Bronze scope):
- No Gmail or WhatsApp integration (Silver tier)
- No MCP servers (Silver tier)
- No external API calls
- No payments or social media

USER STORY:
As a user, I drag a text file into my /Inbox folder. The watcher detects it, creates a task file in /Needs_Action. I run Claude Code and it reads the task, follows the SKILL.md instructions, writes a response plan in /Done, and updates my Dashboard.md — all automatically.

## Response snapshot

Created a comprehensive specification for the Bronze-tier Personal AI Employee. The spec defines the system as a local automation system using Claude Code and Obsidian to monitor tasks, process them, and generate structured outputs. It includes six main features: vault structure, dashboard, company handbook, filesystem watcher, agent skills, and Claude Code integration. The specification includes detailed functional and non-functional requirements, technical requirements, constraints, and assumptions.

## Outcome

- ✅ Impact: Created foundational specification for Bronze-tier AI employee system
- 🧪 Tests: No tests required for specification creation
- 📁 Files: Created specs/ai_employee/spec.md with complete feature specification
- 🔁 Next prompts: Ready for planning and implementation of the AI employee system
- 🧠 Reflection: Specification captures all core features and constraints of the bronze tier system

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin planning implementation based on this specification