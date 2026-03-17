# Quickstart Guide: Gold Tier Features

This guide provides instructions for setting up and using the Gold tier features of the Personal AI Employee system.

## Prerequisites

Before using the Gold tier features, ensure you have:

1. **Environment Configuration**: Copy `.env.example` to `.env` and fill in the required API keys
2. **Vault Structure**: Ensure your vault has the required folder structure
3. **API Access**: Obtain API credentials for Twitter, Facebook/Instagram, and Odoo

## Environment Setup

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Required environment variables for Gold tier features:

### Twitter/X API Configuration
```
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_SECRET=your_twitter_access_token_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
```

### Facebook/Instagram API Configuration
```
FACEBOOK_ACCESS_TOKEN=your_facebook_access_token
FACEBOOK_PAGE_ID=your_facebook_page_id
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token
INSTAGRAM_ACCOUNT_ID=your_instagram_account_id
```

### Odoo API Configuration
```
ODOO_URL=your_odoo_instance_url
ODOO_DB=your_odoo_database_name
ODOO_USERNAME=your_odoo_username
ODOO_PASSWORD=your_odoo_password
```

## Feature Usage

### 1. Ralph Wiggum Loop (Autonomous Task Completion)

The Ralph Wiggum Loop continuously monitors the `Needs_Action` folder and processes tasks automatically.

**To use:**
1. Place task files in the `AI_Employee_Vault/Needs_Action/` folder
2. The AI will process each task using gemma-3-27b-it model
3. If a task is incomplete, it will retry up to 10 times
4. Completed tasks are moved to the `Done` folder
5. All iterations are logged with timestamps and status

**Configuration options:**
- Maximum retry attempts: 10 (configurable via `MAX_RETRY_ATTEMPTS`)
- Maximum retry duration: 24 hours (configurable via `MAX_RETRY_DURATION_HOURS`)

### 2. Social Media Management (Twitter/X, Facebook, Instagram)

#### Generating Social Media Content

1. Ensure your `Company_Handbook.md` contains relevant business context
2. Run the social media content generator:
   ```bash
   python -m src.twitter_poster
   python -m src.social_media_poster
   ```
3. Generated content will appear in the `Pending_Approval` folder

#### Approving and Posting Content

1. Review the generated content in the `Pending_Approval` folder
2. Move approved content to the `Approved` folder
3. The system will automatically post approved content to the respective platforms
4. Posted content will be moved to the `Done` folder

**Rate Limits:**
- Twitter: Maximum 5 posts per day
- Facebook: Maximum 3 posts per day
- Instagram: Maximum 3 posts per day

### 3. Odoo Accounting Integration

#### Creating Invoices

1. Prepare invoice information in a structured format
2. Place the invoice request in the `Pending_Approval` folder
3. Review and move to the `Approved` folder when ready
4. The system will create the invoice in Odoo
5. Processed invoices will be moved to the `Done` folder

**Rate Limits:**
- Odoo invoice creation: Maximum 10 per day

### 4. Weekly Business Audit

The weekly audit system automatically runs every Sunday night at 23:59.

**What it does:**
1. Reads all `Done` files from the past 7 days
2. Reads Odoo financial data from the past week
3. Reads social media activity from the past week
4. Generates a comprehensive audit report as `AUDIT_YYYYMMDD.md`
5. Saves the report in the vault root
6. Feeds data into the Monday CEO Briefing

## Monitoring and Management

### Dashboard Updates

The system automatically updates the `Dashboard.md` file with Gold tier status indicators:
- Ralph Wiggum Loop status
- Twitter/X integration status
- Facebook integration status
- Instagram integration status
- Odoo integration status

### Log Management

- Logs are stored in the `AI_Employee_Vault/Logs/` folder
- Log retention: 90 days (automatic cleanup)
- Daily log files are named with the date format `YYYY-MM-DD.json`

### Approval Management

- Items in `Pending_Approval` folder older than 30 days are auto-rejected
- Regular cleanup ensures the approval queue doesn't become stale

## Dry Run Mode

To test the system without performing actual external actions, set `DRY_RUN=true` in your `.env` file.

## Troubleshooting

### Common Issues

1. **API Rate Limits**: If you encounter rate limit errors, check the logs for rate limit events and adjust your usage accordingly.

2. **Missing Credentials**: Ensure all required environment variables are set.

3. **Connection Issues**: Verify your API credentials and network connectivity.

4. **File Permissions**: Ensure the system has read/write permissions to the vault folders.

### Logs and Debugging

Check the logs in `AI_Employee_Vault/Logs/` for detailed information about system operations and any errors that occur.