---
id: 2
title: "Update constitution silver tier rules"
stage: "constitution"
date: "2026-03-02"
surface: "agent"
model: "claude-sonnet-4-6"
feature: "none"
branch: "master"
user: "abdullah"
command: "sp.constitution"
labels: ["constitution", "silver-tier", "governance"]
links:
  spec: "null"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - ".specify/memory/constitution.md"
tests: []
---

# Update constitution silver tier rules

## User Input
```
Update existing constitution to add Silver tier rules:
1. Gmail API credentials stored in .env only, never in vault
2. WhatsApp automation via Playwright - always ask human approval before replying
3. LinkedIn posts go to Pending_Approval folder first, never auto-post
4. Email replies require human approval for unknown contacts
5. All new watchers follow base_watcher.py pattern
6. Rate limiting: max 10 emails processed per run, max 3 LinkedIn posts per day
```

## Response Summary
Updated the Personal AI Employee Constitution to add Silver tier rules as requested. The changes included:

1. Added six new principles (IX-XIV) covering the Silver tier requirements:
   - Gmail credentials storage in .env only
   - WhatsApp automation with human approval
   - LinkedIn posts requiring approval before posting
   - Email replies for unknown contacts requiring approval
   - Watcher pattern compliance with base_watcher.py
   - Rate limiting for emails and LinkedIn posts

2. Updated existing sections to incorporate Silver tier constraints

3. Incremented version from 1.0.0 to 1.1.0 to reflect the addition of new principles

4. Updated the last amended date to today (2026-03-03-02)

The constitution now includes comprehensive Silver tier governance while maintaining all existing Bronze tier principles.

## Outcome
Constitution successfully updated with Silver tier rules while preserving all existing principles and maintaining proper governance structure.