# Silver Tier Features - Personal AI Employee Specification

## Overview

This specification defines the Silver tier features for the Personal AI Employee system. These features extend the Bronze tier capabilities to include Gmail integration, email automation, and LinkedIn posting capabilities, while maintaining the human-in-the-loop approach and local-first architecture.

## Scope

### In Scope
- Gmail watcher to monitor unread important emails
- Email reply drafting using AI assistance
- LinkedIn post generation and approval workflow
- Human-in-the-loop approval for external communications
- Integration with existing vault structure and dashboard
- Rate limiting for external communications

### Out of Scope
- Direct email sending without human approval (except approved workflow)
- Automatic LinkedIn posting without approval
- Integration with other email providers besides Gmail
- WhatsApp or SMS messaging (planned for Gold tier)

## User Scenarios

### Scenario 1: Gmail Monitoring and Response
As a user, I want the AI employee to monitor my Gmail for important unread emails, draft appropriate responses using AI, and wait for my approval before sending. This saves me time on routine correspondence while maintaining control over what gets sent.

### Scenario 2: LinkedIn Business Post Generation
As a user, I want the AI employee to generate weekly business-related LinkedIn posts based on my preferences, submit them for my approval, and post them only after I explicitly approve them. This helps maintain my professional presence without daily effort.

### Scenario 3: Human-in-the-Loop Approval
As a user, I want to maintain full control over external communications by reviewing and approving all AI-generated content before it goes out, ensuring brand consistency and preventing inappropriate content.

## Functional Requirements

### FR1: Gmail Watcher
- The system SHALL monitor Gmail for all unread emails using the Gmail API
- The system SHALL process all unread emails and later categorize by importance level
- The system SHALL save each email as a .md file in the Needs_Action folder
- The email file SHALL include: sender, subject, date, and email body snippet
- The system SHALL mark emails as read after processing them
- The system SHALL use OAuth2 for secure Gmail API access

### FR2: Email Reply Drafting
- The system SHALL draft email replies using Gemini AI based on the original email content
- The system SHALL save draft replies to the Pending_Approval folder
- The system SHALL NOT send any emails without human approval
- The system SHALL only send emails after a human moves the file to the Approved folder

### FR3: LinkedIn Post Generation
- The system SHALL generate business posts using Gemini AI with configurable frequency (daily, weekly, monthly) with weekly as default
- The system SHALL generate posts based on trending topics in the user's industry
- The system SHALL save post drafts to the Pending_Approval folder
- The system SHALL post to LinkedIn only after human approval
- The system SHALL use LinkedIn API for posting

### FR4: Human-in-the-Loop Workflow
- The system SHALL monitor the Approved folder for approved files
- The system SHALL execute approved actions automatically
- The system SHALL move processed files to the Done folder
- The system SHALL log all actions to the Logs folder with timestamp, action type, success/failure status, and error details when applicable

### FR5: Rate Limiting
- The system SHALL limit email processing to maximum 10 emails per run
- The system SHALL limit LinkedIn posts to maximum 3 per day
- The system SHALL enforce these limits to prevent spam and API abuse
- If an email fails to process, it remains in Needs_Action with error details and continues with other emails

## Non-Functional Requirements

### Security Requirements
- Gmail credentials MUST be stored in .env file only, never in the vault
- All API communications MUST use secure connections (HTTPS/TLS)
- OAuth2 tokens MUST be handled securely with proper refresh mechanisms

### Performance Requirements
- Email processing SHOULD complete within 30 seconds per email
- LinkedIn post generation SHOULD complete within 10 seconds
- System SHOULD handle up to 100 pending approval items without performance degradation

### Reliability Requirements
- System MUST log all actions for audit trail
- System MUST implement fail-safe mechanisms that pause on errors
- System MUST maintain data integrity during processing

## Success Criteria

- Users spend 70% less time on routine email correspondence
- LinkedIn posts are generated consistently (at least 1 per week)
- Zero unauthorized external communications are sent without human approval
- 95% of approval workflows complete within 24 hours of draft creation
- System maintains 99% uptime during business hours

## Key Entities

### Email Entity
- Sender: email address of the sender
- Subject: subject line of the email
- Date: timestamp when email was received
- Body Snippet: first 500 characters of email content
- Status: current processing state (unread, needs_action, pending_approval, approved, done)

### LinkedIn Post Entity
- Content: the generated post content
- Topic: the subject/theme of the post
- Date Created: timestamp when post was generated
- Status: current processing state (draft, pending_approval, approved, posted)

### Approval Entity
- Type: the type of action (email_reply, linkedin_post)
- Content: the content to be approved
- Date Submitted: timestamp when submitted for approval
- Date Approved: timestamp when approved (null if not approved)
- Status: current approval state (pending, approved, rejected)

## Assumptions

- User has Gmail account with appropriate API access configured
- User has LinkedIn account with appropriate API access configured
- User will regularly review and approve content in the Pending_Approval folder
- User has reliable internet connection for API communications
- Rate limits specified are sufficient for typical usage patterns

## Constraints

- All data processing occurs locally on the user's machine
- All external API credentials are stored in .env file only
- No external communications occur without explicit human approval
- System must comply with Gmail and LinkedIn API usage policies
- All actions must be logged for audit trail compliance

## Clarifications

### Session 2026-03-02

- Q: How frequently are LinkedIn posts generated? → A: User-configurable frequency (daily, weekly, monthly) with weekly as default
- Q: How are "important" emails defined? → A: All unread emails are processed, with the system later categorizing by importance level
- Q: How should the system handle email processing failures? → A: If an email fails to process, it remains in Needs_Action with error details and continues with other emails
- Q: What content sources should drive LinkedIn post generation? → A: LinkedIn posts are generated based on trending topics in the user's industry
- Q: What details should be included in system logs? → A: Logs should include timestamp, action type, success/failure status, and error details when applicable

## Dependencies

- Gmail API access with OAuth2 configuration
- LinkedIn API access with appropriate permissions
- Existing vault structure with Needs_Action, Pending_Approval, Approved, and Done folders
- Existing dashboard system for status reporting
- Gemini AI access with valid API key