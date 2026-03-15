# Data Model: Gold Tier Features

This document describes the key entities and their relationships for the Gold tier features of the Personal AI Employee system.

## Entities

### 1. Task Entity (Ralph Wiggum Loop)

Represents a task that undergoes autonomous processing with retry logic.

**Attributes:**
- `task_id`: Unique identifier for the task
- `content`: The task content to be processed
- `iteration_count`: Number of processing attempts (max 10)
- `status`: Current processing state (needs_action, processing, done, failed, needs_retry)
- `last_attempt`: Timestamp of last processing attempt
- `result`: Outcome of the processing attempt
- `created_at`: Timestamp when task was created
- `attempts`: Number of attempts made

**Relationships:**
- Transitions through folder states: Needs_Action → Done

### 2. Social Media Post Entity

Represents content for Twitter/X, Facebook, or Instagram with approval workflow.

**Attributes:**
- `post_id`: Unique identifier for the post
- `platform`: Target platform (twitter, facebook, instagram)
- `content`: The generated post content
- `status`: Current processing state (draft, pending_approval, approved, posted)
- `approval_date`: Timestamp when approved (null if not approved)
- `post_date`: Timestamp when posted (null if not posted)
- `created_at`: Timestamp when post was created
- `hashtags`: List of hashtags associated with the post
- `emojis`: List of emojis associated with the post

**Relationships:**
- Moves through folder states: Pending_Approval → Approved → Done

### 3. Invoice Entity (Odoo Integration)

Represents an invoice for creation in the Odoo accounting system.

**Attributes:**
- `invoice_id`: Unique identifier from Odoo system (after creation)
- `customer`: Customer information (name, email, phone)
- `line_items`: List of products/services and amounts
- `status`: Current state (pending_approval, approved, created_in_odoo, failed)
- `approval_date`: Timestamp when approved for creation
- `creation_date`: Timestamp when created in Odoo
- `created_at`: Timestamp when invoice was created
- `due_date`: Due date for the invoice
- `reference`: Reference number for the invoice
- `total_amount`: Total amount of the invoice

**Relationships:**
- Moves through folder states: Pending_Approval → Approved → Done
- Associated with Odoo customer (partner) and products

### 4. Audit Report Entity

Represents the weekly business audit report.

**Attributes:**
- `report_id`: Unique identifier based on date (YYYYMMDD)
- `period_start`: Start date of audit period
- `period_end`: End date of audit period
- `content`: Compiled audit information
- `generated_date`: Timestamp when report was generated
- `status`: Current state (generated, reviewed)
- `tasks_completed`: Number of tasks completed in the period
- `revenue_generated`: Total revenue generated in the period
- `social_media_activity`: Summary of social media activity in the period

**Relationships:**
- Contains aggregated data from: Task, Invoice, Social Media Post entities
- Saved as file with name pattern: AUDIT_YYYYMMDD.md

### 5. Rate Limit Entity

Tracks usage against defined limits for various services.

**Attributes:**
- `service`: Service name (twitter, facebook, instagram, odoo)
- `current_count`: Current count toward the limit
- `max_limit`: Maximum allowed limit
- `date`: Date for the count tracking
- `last_updated`: Timestamp of last update

**Relationships:**
- Associated with API calls for each service

### 6. Approval Queue Entity

Represents the Pending_Approval folder containing items awaiting human approval.

**Attributes:**
- `item_id`: Unique identifier for the item
- `content`: Content of the item awaiting approval
- `type`: Type of item (social_media_post, invoice, task_result)
- `submitted_date`: Timestamp when submitted for approval
- `expires_date`: Timestamp when auto-rejection occurs (based on approval expiration days)
- `status`: Current state (pending, approved, rejected)

**Relationships:**
- Moves to Approved folder when approved
- Moves to Done folder when processed
- Connected to Social Media Post, Invoice, and Task entities

## Relationships

### Folder-Based State Transitions

The system uses a folder-based state management approach:

```
Needs_Action (Task) → Done (Task)
Pending_Approval (Social Media/Invoice) → Approved → Done
```

### Approval Workflow

Most Gold tier entities follow a human-in-the-loop approval workflow:
1. Items are created in `Pending_Approval` folder
2. Human reviews and moves to `Approved` folder if acceptable
3. System processes approved items and moves to `Done` folder

### Data Aggregation

The Audit Report entity aggregates data from:
- Task entities (for task completion metrics)
- Invoice entities (for financial data)
- Social Media Post entities (for social media activity)

## Constraints

1. **Retry Limit**: Tasks in Ralph Wiggum Loop have a maximum of 10 retry attempts
2. **Time Limit**: Tasks have a maximum processing duration of 24 hours
3. **Rate Limits**:
   - Twitter: 5 posts per day
   - Facebook: 3 posts per day
   - Instagram: 3 posts per day
   - Odoo: 10 invoice creations per day
4. **Approval Timeout**: Items in Pending_Approval expire after 30 days
5. **Log Retention**: Logs are retained for 90 days

## Indexes

For efficient querying and processing:
- Task entities indexed by `task_id` and `status`
- Social Media Post entities indexed by `platform` and `status`
- Invoice entities indexed by `status` and `approval_date`
- Audit Report entities indexed by `period_start` and `period_end`
- Rate Limit entities indexed by `service` and `date`