# Tasks: Gold Tier Features for Personal AI Employee

**Feature**: Gold Tier Features
**Branch**: `1-gold-tier`
**Generated**: 2026-03-07
**Spec**: [specs/1-gold-tier/spec.md](../specs/1-gold-tier/spec.md)
**Plan**: [specs/1-gold-tier/plan.md](../specs/1-gold-tier/plan.md)

## Implementation Strategy

**MVP Goal**: Implement US1 (Ralph Wiggum Loop) as the foundational autonomous task processing capability, which will serve as the basis for other Gold tier features.

**Delivery Approach**: Incremental delivery by user story with each phase delivering independently testable functionality that maintains backward compatibility with existing Bronze/Silver tier features.

## Dependencies

- **US1 (P1)**: No dependencies - implements core autonomous task processing
- **US2 (P2)**: Depends on foundational components from Phase 2
- **US3 (P3)**: Depends on foundational components from Phase 2
- **US4 (P4)**: Depends on US2 and US3 for social media data, US3 for accounting data

## Parallel Execution Examples

- **Within US2**: Twitter poster implementation can run in parallel with Facebook/Instagram poster implementation (different files, no shared dependencies)
- **Within US3**: Odoo integration can be developed in parallel with other features since it operates on separate systems
- **Across US2/US3**: Social media and accounting features can be developed simultaneously as they have separate data flows

---

## Phase 1: Setup (Project Initialization)

**Goal**: Initialize project structure and dependencies for Gold tier features

- [X] T001 Create src directory if it doesn't exist
- [X] T002 Update pyproject.toml with Gold tier dependencies (tweepy, schedule, watchdog)
- [X] T003 Create .env.example with all required environment variables for Gold tier features
- [X] T004 Create scripts directory and add process_tasks_gold.bat script
- [X] T005 Create logs directory structure if not exists

---

## Phase 2: Foundational (Blocking Prerequisites)

**Goal**: Establish common infrastructure components needed by multiple user stories

- [X] T010 Create common AI processing module in src/ai_utils.py with gemma-3-27b-it integration and fallback mechanisms
- [X] T011 [P] Create logging utility in src/logger.py for audit trail compliance
- [X] T012 [P] Create configuration manager in src/config.py for environment variables
- [X] T013 [P] Create rate limiter utility in src/rate_limiter.py with tracking for Twitter (5/day), Facebook (3/day), Instagram (3/day), Odoo (10/day)
- [X] T014 [P] Create file utils in src/file_utils.py for vault folder monitoring and state management
- [X] T015 [P] Extend approved_watcher.py to handle Gold tier approved actions
- [X] T016 Create base watcher class in src/base_watcher.py that extends existing functionality
- [X] T017 Update dashboard_updater.py to include Gold tier status indicators

---

## Phase 3: US1 - Autonomous Task Completion (Ralph Wiggum Loop)

**Goal**: Implement the Ralph Wiggum loop that monitors Needs_Action folder and processes tasks with AI, retrying up to 10 times before stopping.

**Independent Test Criteria**:
- Place a task file in Needs_Action folder
- Verify AI processes the task using gemma-3-27b-it model
- If task is incomplete, verify it retries up to 10 times
- Only stops when task moves to Done folder
- All iterations are logged with timestamps and status

- [X] T020 Create ralph_loop.py with file monitoring for Needs_Action folder
- [X] T021 [P] Implement task processing function using gemma-3-27b-it AI model
- [X] T022 [P] Implement retry logic with max 10 attempts and exponential backoff
- [X] T023 [P] Implement state tracking for tasks (iteration count, status, timestamps)
- [X] T024 [P] Implement logging for each iteration with timestamp and status
- [X] T025 [P] Add 24-hour maximum retry period before marking task as failed
- [X] T026 [P] Implement file movement from Needs_Action to Done when complete
- [X] T027 Create task state persistence in src/task_state_manager.py
- [X] T028 Add Ralph loop monitoring to main application entry point

---

## Phase 4: US2 - Social Media Management (Twitter/X, Facebook, Instagram)

**Goal**: Implement AI-powered social media content generation with human approval workflow and rate limiting.

**Independent Test Criteria**:
- Provide business context from Company_Handbook.md
- Verify AI generates appropriate Twitter content with hashtags
- Verify AI generates Facebook/Instagram content with hashtags and emojis
- Verify all content goes to Pending_Approval folder
- Verify content only posts after human approval
- Verify rate limits are enforced (Twitter 5/day, Facebook/Instagram 3/day)

- [X] T030 Create twitter_poster.py with AI-powered tweet generation from Company_Handbook.md
- [X] T031 [P] Implement tweet draft saving to Pending_Approval folder
- [X] T032 [P] Implement Twitter API v2 posting functionality using tweepy
- [X] T033 [P] Add Twitter rate limiting (max 5 posts per day) using rate_limiter utility
- [X] T034 Create social_media_poster.py with AI-powered Facebook/Instagram post generation
- [X] T035 [P] Implement platform-appropriate content formatting (hashtags, emojis)
- [X] T036 [P] Implement Facebook/Instagram draft saving to Pending_Approval folder
- [X] T037 [P] Implement Meta Graph API posting functionality for Facebook/Instagram
- [X] T038 [P] Add Facebook/Instagram rate limiting (max 3 posts per day per platform)
- [X] T039 [P] Add logging for all social media activities
- [X] T040 [P] Implement approval workflow in approved_watcher.py for social media posts
- [X] T041 Update Company_Handbook.md parser in src/handbook_parser.py for social media context

---

## Phase 5: US3 - Business Accounting (Odoo Integration)

**Goal**: Implement Odoo accounting integration for invoice creation and financial reporting with human approval workflow.

**Independent Test Criteria**:
- Connect to local Odoo Community instance via JSON-RPC API
- Verify invoice creation based on approved requests
- Verify transactions can be read and reports generated
- Verify all accounting entries go to Pending_Approval first
- Verify human approval is required before posting to Odoo
- Verify integration with CEO Briefing system

- [X] T045 Create odoo_integration.py with JSON-RPC API connection to Odoo
- [X] T046 [P] Implement invoice creation functionality with validation
- [X] T047 [P] Implement transaction reading and report generation
- [X] T048 [P] Implement pending approval workflow for accounting entries
- [X] T049 [P] Add Odoo rate limiting (max 10 invoice creations per day)
- [X] T050 [P] Add logging for all Odoo activities
- [X] T051 [P] Implement approval workflow in approved_watcher.py for Odoo entries
- [X] T052 [P] Create invoice data model based on spec requirements
- [X] T053 [P] Integrate with CEO Briefing system for financial summaries
- [X] T054 Create odoo_api_client.py for safe, reusable Odoo API calls

---

## Phase 6: US4 - Weekly Business Intelligence

**Goal**: Implement automated weekly audit system that runs every Sunday night and generates comprehensive business reports.

**Independent Test Criteria**:
- Verify system runs automatically every Sunday night via scheduler
- Verify system reads Done files from past 7 days
- Verify system reads Odoo financial data from past week
- Verify system reads social media activity from past week
- Verify comprehensive audit report is generated in markdown format
- Verify report is saved as AUDIT_YYYYMMDD.md in vault
- Verify data feeds into Monday CEO Briefing

**Dependencies**: Requires US2 (social media) and US3 (accounting) to have data available

- [X] T055 Create weekly_audit.py with scheduled execution for Sunday night
- [X] T056 [P] Implement Done files reader for past 7 days
- [X] T057 [P] Implement Odoo financial data reader for past week
- [X] T058 [P] Implement social media activity reader for past week
- [X] T059 [P] Create audit report generator in markdown format
- [X] T060 [P] Implement file saving as AUDIT_YYYYMMDD.md in vault
- [X] T061 [P] Integrate with CEO Briefing system
- [X] T062 [P] Add key metrics and insights to audit report
- [X] T063 [P] Implement 5-minute maximum processing time for reports
- [X] T064 Create audit_data_aggregator.py for collecting data from multiple sources

---

## Phase 7: Polish & Cross-Cutting Concerns

**Goal**: Complete integration, testing, and refinement of all Gold tier features

- [X] T070 Add 90-day log retention policy and cleanup functionality
- [X] T071 Implement 30-day auto-rejection for unapproved pending items
- [X] T072 Add dry-run mode capability to all Gold tier features
- [X] T073 Update README.md with Gold tier feature documentation
- [X] T074 Create quickstart guide for Gold tier features in quickstart.md
- [X] T075 Add error handling and fail-safe mechanisms to all components
- [X] T076 Implement performance monitoring for all features (30s Ralph loop, 10s social media gen, 5s Odoo ops)
- [X] T077 Add comprehensive logging for audit trail compliance
- [X] T078 Create data-model.md documenting all entities and relationships
- [X] T079 Update existing tests to include Gold tier functionality
- [X] T080 Perform end-to-end testing of all user stories