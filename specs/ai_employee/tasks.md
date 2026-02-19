---
description: "Task list for Personal AI Employee implementation"
---

# Tasks: Personal AI Employee

**Input**: Design documents from `/specs/ai_employee/`
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

- [X] T001 Create project structure per implementation plan in personal-ai-employee/
- [X] T002 [P] Initialize Python 3.13 project with uv and pyproject.toml
- [X] T003 [P] Create .env.example file with required environment variables
- [X] T004 [P] Create .gitignore file excluding sensitive files and logs
- [X] T005 Create README.md with project overview and setup instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Install python-watchdog dependency for filesystem monitoring
- [X] T007 Install python-dotenv dependency for environment management
- [X] T008 Create base_watcher.py with abstract base class in src/base_watcher.py
- [X] T009 Create directory structure for AI_Employee_Vault in personal-ai-employee/AI_Employee_Vault/
- [X] T010 Create Inbox, Needs_Action, Done, Logs, Pending_Approval, Approved folders
- [X] T011 Create initial Dashboard.md file in AI_Employee_Vault/Dashboard.md
- [X] T012 Create initial Company_Handbook.md file in AI_Employee_Vault/Company_Handbook.md
- [X] T013 Create skills directory and initial skill files in AI_Employee_Vault/skills/

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Filesystem Watcher Implementation (Priority: P1) 🎯 MVP

**Goal**: Implement a Python filesystem watcher that monitors the Inbox folder and copies new files to Needs_Action with metadata sidecar

**Independent Test**: When a file is placed in the Inbox folder, it should be copied to Needs_Action with a corresponding metadata file and logged appropriately

### Implementation for User Story 1

- [X] T014 [P] [US1] Create filesystem_watcher.py with WatchdogObserver implementation in src/filesystem_watcher.py
- [X] T015 [US1] Implement file copy functionality from Inbox to Needs_Action in src/filesystem_watcher.py
- [X] T016 [US1] Implement metadata sidecar file creation with timestamp and status in src/filesystem_watcher.py
- [X] T017 [US1] Implement JSON logging to Logs folder in src/filesystem_watcher.py
- [X] T018 [US1] Add fail-safe error handling that pauses the watcher on errors in src/filesystem_watcher.py
- [X] T019 [US1] Add dry-run mode support with DRY_RUN environment variable in src/filesystem_watcher.py
- [X] T020 [US1] Create initial SKILL_triage.md file in AI_Employee_Vault/skills/SKILL_triage.md
- [X] T021 [US1] Create initial SKILL_dashboard_update.md file in AI_Employee_Vault/skills/SKILL_dashboard_update.md

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Dashboard and Status Updates (Priority: P2)

**Goal**: Implement Dashboard.md that shows counts of pending items, recent activity, and system status

**Independent Test**: When files are processed, the Dashboard.md should update with current status information

### Implementation for User Story 2

- [X] T022 [P] [US2] Implement dashboard update function in src/dashboard_updater.py
- [X] T023 [US2] Add logic to count items in each status folder (Inbox, Needs_Action, Done, etc.) in src/dashboard_updater.py
- [X] T024 [US2] Add recent activity logging to Dashboard.md in src/dashboard_updater.py
- [X] T025 [US2] Update filesystem watcher to call dashboard update function in src/filesystem_watcher.py
- [X] T026 [US2] Create SKILL_response_formatting.md file in AI_Employee_Vault/skills/SKILL_response_formatting.md
- [X] T027 [US2] Create SKILL_approval_process.md file in AI_Employee_Vault/skills/SKILL_approval_process.md

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Claude Code Integration (Priority: P3)

**Goal**: Integrate Claude Code to process files in Needs_Action folder following skill instructions

**Independent Test**: When Claude Code is run, it should process files in Needs_Action, update Dashboard.md, and move files to appropriate folders

### Implementation for User Story 3

- [X] T028 [P] [US3] Create run_claude.sh script in scripts/run_claude.sh
- [X] T029 [US3] Implement logic to read files from Needs_Action folder in scripts/run_claude.sh
- [X] T030 [US3] Add Claude Code integration to process files following skill instructions in scripts/run_claude.sh
- [X] T031 [US3] Implement file movement from Needs_Action to Done folder after processing in scripts/run_claude.sh
- [X] T032 [US3] Add support for approval workflow (Pending_Approval/Approved folders) in scripts/run_claude.sh
- [X] T033 [US3] Update dashboard after Claude Code processing in scripts/run_claude.sh
- [X] T034 [US3] Add logging of Claude Code actions to Logs folder in scripts/run_claude.sh

**Checkpoint**: All user stories should now be independently functional

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T035 [P] Update README.md with complete usage instructions
- [X] T036 [P] Create PM2 configuration file for running the watcher continuously
- [X] T037 [P] Add cron job/task scheduler setup instructions to README.md
- [X] T038 Create research.md with findings from implementation
- [X] T039 Create data-model.md documenting the vault file structure
- [X] T040 Create quickstart.md with step-by-step setup instructions
- [X] T041 Run complete system validation to ensure all components work together

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

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
Task: "Create filesystem_watcher.py with WatchdogObserver implementation in src/filesystem_watcher.py"
Task: "Create initial SKILL_triage.md file in AI_Employee_Vault/skills/SKILL_triage.md"
Task: "Create initial SKILL_dashboard_update.md file in AI_Employee_Vault/skills/SKILL_dashboard_update.md"
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
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
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