# Gold Tier Features - Personal AI Employee Specification

## Overview

This specification defines the Gold tier features for the Personal AI Employee system. These features extend the Silver tier capabilities to include advanced automation loops, social media integration (Twitter/X, Facebook, Instagram), business accounting integration (Odoo), and automated weekly business auditing, while maintaining the human-in-the-loop approach and local-first architecture.

## Scope

### In Scope
- Ralph Wiggum autonomous task completion loop
- Twitter/X integration with AI-generated tweets
- Facebook and Instagram integration with AI-generated posts
- Odoo accounting integration for financial entries
- Weekly business audit automation
- Human-in-the-loop approval for all external communications
- Rate limiting and safety controls for all new features
- Integration with existing vault structure and dashboard

### Out of Scope
- WhatsApp automation (planned for Platinum tier)
- Direct payment processing
- Advanced machine learning model training
- Cloud-based processing (all processing remains local)
- Automatic posting without human approval (except approved workflow)

## User Scenarios

### Scenario 1: Autonomous Task Completion (Ralph Wiggum Loop)
As a user, I want the AI employee to autonomously complete tasks with minimal supervision, retrying up to 10 times when needed, while keeping me informed of progress. This allows routine tasks to be completed automatically while maintaining control over the process.

### Scenario 2: Social Media Management (Twitter/X, Facebook, Instagram)
As a user, I want the AI employee to generate relevant social media content using AI, submit it for my approval, and post it only after I explicitly approve it. This helps maintain my online presence without daily effort while ensuring brand consistency.

### Scenario 3: Business Accounting (Odoo Integration)
As a user, I want the AI employee to interact with my Odoo accounting system to create invoices and read financial data, but only after I approve each action. This helps automate routine accounting tasks while maintaining financial control.

### Scenario 4: Weekly Business Intelligence
As a user, I want the AI employee to automatically compile a comprehensive weekly audit every Sunday night, pulling together information from completed tasks, financial data, and social media activity. This gives me a complete picture of business activity without manual compilation.

## Functional Requirements

### FR1: Ralph Wiggum Loop
- The system SHALL monitor the Needs_Action folder for new tasks
- The system SHALL process each task using Gemini AI with gemma-3-27b-it model
- If a task is incomplete, the system SHALL retry up to 10 times before stopping
- The system SHALL only stop processing when the task moves to Done
- The system SHALL log each iteration with timestamp and status
- The system SHALL maintain a maximum of 10 retries to prevent infinite loops

### FR2: Twitter/X Integration
- The system SHALL generate tweets using Gemini AI based on business context from Company_Handbook.md
- The system SHALL save tweet drafts to the Pending_Approval folder
- The system SHALL NOT post to Twitter/X without human approval
- The system SHALL post to Twitter/X only after a human moves the file to Approved folder
- The system SHALL use Twitter API v2 for posting
- The system SHALL log all Twitter/X activity to the Logs folder

### FR3: Facebook & Instagram Integration
- The system SHALL generate social media posts using Gemini AI for both Facebook and Instagram
- The system SHALL create content appropriate for each platform's audience and format
- The system SHALL save post drafts to the Pending_Approval folder
- The system SHALL NOT post to Facebook or Instagram without human approval
- The system SHALL post to Facebook/Instagram only after human approval
- The system SHALL include relevant hashtags and emojis in generated content
- The system SHALL use Meta Graph API for posting
- The system SHALL log all social media activity to the Logs folder

### FR4: Odoo Accounting Integration
- The system SHALL connect to local Odoo Community instance using JSON-RPC API
- The system SHALL create invoices based on approved requests
- The system SHALL read transactions and generate financial reports
- All accounting entries MUST be saved to Pending_Approval folder first
- Human approval MUST be obtained before posting any financial entries to Odoo
- The system SHALL integrate with CEO Briefing for financial summaries
- The system SHALL validate all financial data before submission

### FR5: Weekly Business Audit
- The system SHALL run automatically every Sunday night via scheduler
- The system SHALL read all Done files from the past 7 days
- The system SHALL read Odoo financial data from the past week
- The system SHALL read social media activity from the past week
- The system SHALL generate a comprehensive audit report in Markdown format
- The system SHALL save the report as AUDIT_YYYYMMDD.md in the Vault
- The system SHALL feed the audit data into Monday CEO Briefing
- The system SHALL include key metrics and insights in the audit report

### FR6: Human-in-the-Loop Workflow
- The system SHALL monitor the Approved folder for approved files
- The system SHALL execute approved actions automatically
- The system SHALL move processed files to the Done folder
- The system SHALL log all actions to the Logs folder with timestamp, action type, success/failure status, and error details when applicable
- The system SHALL maintain audit trail for all actions taken

### FR7: Rate Limiting & Safety Controls
- The system SHALL enforce rate limiting for all new Gold tier features
- Twitter/X: maximum 5 posts per day
- Facebook: maximum 3 posts per day
- Instagram: maximum 3 posts per day
- Odoo invoice creation: maximum 10 per day
- The system SHALL implement safeguards to prevent spam and API abuse
- The system SHALL pause processing if rate limits are exceeded

## Non-Functional Requirements

### Security Requirements
- All social media API credentials must be stored in .env file only, never in vault
- All Odoo credentials must be stored in .env file only, never in vault
- All external API communications must use secure connections (HTTPS/TLS)
- OAuth2 tokens must be handled securely with proper refresh mechanisms
- All credentials must be encrypted at rest

### Performance Requirements
- Ralph Wiggum loop processing: maximum 30 seconds per task iteration
- Social media post generation: maximum 10 seconds per post
- Odoo API calls: maximum 5 seconds per request
- Weekly audit generation: maximum 5 minutes for complete report
- System shall handle up to 50 pending approval items without performance degradation

### Reliability Requirements
- System must log all actions for audit trail
- System must implement fail-safe mechanisms that pause on errors
- System must maintain data integrity during processing
- Rate limiting must be enforced to prevent API quota exhaustion
- Retry mechanisms must have exponential backoff to prevent overwhelming services

## Success Criteria

- Users spend 80% less time on routine social media posting
- All accounting entries are properly approved before posting to Odoo
- Weekly audit reports are generated consistently every Sunday
- Zero unauthorized external communications are sent without human approval
- 95% of autonomous tasks complete successfully within 5 iterations
- System maintains 99% uptime during business hours

## Key Entities

### Task Entity (Ralph Wiggum Loop)
- Task ID: unique identifier for the task
- Content: the task content to be processed
- Iteration Count: number of processing attempts (max 10)
- Status: current processing state (needs_action, processing, done, failed)
- Last Attempt: timestamp of last processing attempt
- Result: outcome of the processing attempt

### Social Media Post Entity
- Post ID: unique identifier for the post
- Platform: target platform (twitter, facebook, instagram)
- Content: the generated post content
- Status: current processing state (draft, pending_approval, approved, posted)
- Approval Date: timestamp when approved (null if not approved)
- Post Date: timestamp when posted (null if not posted)

### Invoice Entity (Odoo Integration)
- Invoice ID: unique identifier from Odoo system
- Customer: customer information
- Line Items: list of products/services and amounts
- Status: current state (pending_approval, approved, created_in_odoo, failed)
- Approval Date: timestamp when approved for creation
- Creation Date: timestamp when created in Odoo

### Audit Report Entity
- Report ID: unique identifier based on date (YYYYMMDD)
- Period Start: start date of audit period
- Period End: end date of audit period
- Content: compiled audit information
- Generated Date: timestamp when report was generated
- Status: current state (generated, reviewed)

## Assumptions

- User has Twitter/X developer account with API access configured
- User has Facebook/Instagram business account with API access configured
- User has local Odoo Community instance with appropriate API access
- User will regularly review and approve content in the Pending_Approval folder
- User has reliable internet connection for API communications
- Rate limits specified are sufficient for typical usage patterns

## Constraints

- All data processing occurs locally on the user's machine
- All external API credentials are stored in .env file only
- No external communications occur without explicit human approval
- System must comply with Twitter, Facebook, Instagram, and Odoo API usage policies
- All actions must be logged for audit trail compliance
- All Gold tier features must have dry-run mode capability

## Dependencies

- Twitter API access with appropriate permissions
- Facebook Graph API access with appropriate permissions
- Instagram API access via Facebook Graph API
- Odoo Community instance with JSON-RPC API access
- Existing vault structure with Needs_Action, Pending_Approval, Approved, and Done folders
- Existing dashboard system for status reporting
- Gemini AI access with valid API key
- Scheduled execution capability for weekly audit

## Clarifications

### Session 2026-03-06
- Q: What should be the daily rate limits for social media and accounting features? → A: Standard limits as specified (Twitter 5/day, Facebook/Instagram 3/day, Odoo 10/day)
- Q: Should the system have fallback options if the primary AI model is unavailable? → A: Multiple fallback models if primary fails
- Q: What should be the maximum time period for retry attempts before permanently failing a task? → A: 24 hours maximum retry period
- Q: How long should the system retain logs and processed items before archiving or deletion? → A: 90 days retention