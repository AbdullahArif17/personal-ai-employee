---
description: "Task list for Silver tier features implementation"
---

# Tasks: Silver Tier Features

**Input**: Design documents from `/specs/1-silver-tier/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Update pyproject.toml with Silver tier dependencies
- [X] T002 [P] Install google-api-python-client dependency
- [X] T003 [P] Install google-auth-oauthlib dependency
- [X] T004 [P] Install linkedin-api dependency
- [X] T005 [P] Install playwright dependency
- [X] T006 Update .env.example with Silver tier credentials

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Create gmail_watcher.py extending base_watcher.py pattern in src/gmail_watcher.py
- [X] T008 Create Approved folder in AI_Employee_Vault/Approved/
- [X] T009 Update dashboard_updater.py to monitor Approved folder
- [X] T010 Create approved_watcher.py based on base_watcher pattern in src/approved_watcher.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Gmail Watcher Implementation (Priority: P1) 🎯 MVP

**Goal**: Implement a Python Gmail watcher that monitors Gmail for unread emails and saves them as .md files in Needs_Action folder

**Independent Test**: When new emails arrive in Gmail, they should appear as .md files in the Needs_Action folder with sender, subject, date, and body snippet

### Implementation for User Story 1

- [X] T011 [P] [US1] Create gmail_watcher.py with Gmail API integration in src/gmail_watcher.py
- [X] T012 [US1] Implement OAuth2 authentication for Gmail in src/gmail_auth.py
- [X] T013 [US1] Implement email retrieval from Gmail API in src/gmail_watcher.py
- [X] T014 [US1] Implement saving emails as .md files in Needs_Action folder in src/gmail_watcher.py
- [X] T015 [US1] Include sender, subject, date, and body snippet in saved files in src/gmail_watcher.py
- [X] T016 [US1] Implement marking emails as read after processing in src/gmail_watcher.py
- [X] T017 [US1] Add rate limiting to comply with Gmail API quotas in src/gmail_watcher.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Email MCP Server (Priority: P2)

**Goal**: Implement an email reply drafting system that uses Gemini AI to create responses and saves them to Pending_Approval folder

**Independent Test**: When an email is processed, the system should generate a draft reply using AI and save it to Pending_Approval for human review

### Implementation for User Story 2

- [X] T018 [P] [US2] Create email_mcp.py for email processing in src/email_mcp.py
- [X] T019 [US2] Implement AI-powered email reply generation in src/email_mcp.py
- [X] T020 [US2] Save draft replies to Pending_Approval folder in src/email_mcp.py
- [X] T021 [US2] Implement logic to wait for human approval before sending in src/email_mcp.py
- [X] T022 [US2] Implement email sending functionality after approval in src/email_mcp.py
- [X] T023 [US2] Log all sent emails to Logs folder in src/email_mcp.py
- [X] T024 [US2] Add rate limiting for email processing (max 10 per run) in src/email_mcp.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - LinkedIn Poster (Priority: P3)

**Goal**: Implement LinkedIn post generation system that creates business posts using Gemini AI and submits them for approval

**Independent Test**: When the system runs, it should generate a LinkedIn post based on trending topics and save it to Pending_Approval folder

### Implementation for User Story 3

- [X] T025 [P] [US3] Create linkedin_poster.py for LinkedIn integration in src/linkedin_poster.py
- [X] T026 [US3] Implement OAuth2 authentication for LinkedIn in src/linkedin_auth.py
- [X] T027 [US3] Implement post generation using Gemini AI in src/linkedin_poster.py
- [X] T028 [US3] Generate posts based on trending industry topics in src/linkedin_poster.py
- [X] T029 [US3] Save post drafts to Pending_Approval folder in src/linkedin_poster.py
- [X] T030 [US3] Implement posting to LinkedIn after human approval in src/linkedin_poster.py
- [X] T031 [US3] Add rate limiting (max 3 posts per day) in src/linkedin_poster.py

**Checkpoint**: At this point, User Stories 1, 2 AND 3 should all work independently

---

## Phase 6: User Story 4 - Human-in-the-Loop Workflow (Priority: P4)

**Goal**: Implement the complete approval workflow that monitors Approved folder and executes approved actions

**Independent Test**: When a file is moved to the Approved folder, the system should execute the appropriate action (send email, post to LinkedIn) and move to Done

### Implementation for User Story 4

- [X] T032 [P] [US4] Enhance approved_watcher.py to process approved files in src/approved_watcher.py
- [X] T033 [US4] Implement logic to identify action type from approved files in src/approved_watcher.py
- [X] T034 [US4] Implement execution of approved email sending in src/approved_watcher.py
- [X] T035 [US4] Implement execution of approved LinkedIn posts in src/approved_watcher.py
- [X] T036 [US4] Move processed files to Done folder after execution in src/approved_watcher.py
- [X] T037 [US4] Log all executed actions to Logs folder in src/approved_watcher.py
- [X] T038 [US4] Update dashboard to show approval workflow status in AI_Employee_Vault/Dashboard.md

**Checkpoint**: All user stories should now be independently functional

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T039 [P] Update README.md with Silver tier features documentation
- [X] T040 [P] Create OAuth setup scripts for Gmail and LinkedIn
- [X] T041 Add error handling and retry logic to all watchers
- [X] T042 Add comprehensive logging to all components
- [X] T043 Run complete system validation to ensure all components work together
- [X] T044 Create process_tasks_silver.bat script for Silver tier features

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 for email input
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Depends on US1, US2, US3 for approval workflow

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all parallel tasks for User Story 1 together:
Task: "Create gmail_watcher.py with Gmail API integration in src/gmail_watcher.py"
Task: "Create OAuth2 authentication for Gmail in src/gmail_auth.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
   - Developer D: User Story 4
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence