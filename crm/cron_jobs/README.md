# Customer Cleanup Cron Jobs

This directory contains automated cleanup scripts for the ALX Backend GraphQL CRM system.

## Files

### `clean_inactive_customers.sh`
- **Purpose**: Deletes customers with no orders since a year ago
- **Execution**: Runs via cron job every Sunday at 2:00 AM
- **Logging**: Logs all activities to `/tmp/customer_cleanup_log.txt`
- **Safety**: Uses Django transactions for data consistency

### `customer_cleanup_crontab.txt`
- **Purpose**: Contains the cron job schedule
- **Schedule**: Every Sunday at 2:00 AM (`0 2 * * 0`)
- **Usage**: Copy this line to your system's crontab

### `send_order_reminders.py`
- **Purpose**: Queries GraphQL for orders from the last 7 days and logs reminders
- **Execution**: Runs via cron job daily at 8:00 AM
- **Logging**: Logs reminders to `/tmp/order_reminders_log.txt`
- **Features**: GraphQL integration, comprehensive logging, error handling

### `order_reminders_crontab.txt`
- **Purpose**: Contains the cron job schedule for order reminders
- **Schedule**: Daily at 8:00 AM (`0 8 * * *`)
- **Usage**: Copy this line to your system's crontab

## Django-Crontab Integration

### Heartbeat Logger
The system also includes a django-crontab based heartbeat logger that runs every 5 minutes:

- **Function**: `crm.cron.log_crm_heartbeat`
- **Schedule**: Every 5 minutes (`*/5 * * * *`)
- **Logging**: `/tmp/crm_heartbeat_log.txt`
- **Features**: 
  - Basic heartbeat logging
  - GraphQL endpoint health check
  - Customer count verification
  - Comprehensive error handling

### Stock Update Logger
The system includes a django-crontab based stock update job that runs every 12 hours:

- **Function**: `crm.cron.update_low_stock`
- **Schedule**: Every 12 hours (`0 */12 * * *`)
- **Logging**: `/tmp/low_stock_updates_log.txt`
- **Features**: 
  - Automatically finds products with stock < 10
  - Increments stock by 10 (simulating restocking)
  - GraphQL mutation integration
  - Comprehensive logging of all updates
  - Transaction safety for data consistency

### Django-Crontab Configuration
The cron jobs are configured in `alx_backend_graphql/settings/base.py`:

```python
CRONJOBS = [
    ('*/5 * * * *', 'crm.cron.log_crm_heartbeat'),
    ('0 */12 * * *', 'crm.cron.update_low_stock'),
]
```

## Installation

### 1. Make the shell script executable
```bash
chmod +x crm/cron_jobs/clean_inactive_customers.sh
```

### 2. Install required Python packages
```bash
pip3 install -r requirements.txt
```

### 3. Add cron jobs to system crontab
```bash
# View current crontab
crontab -l

# Edit crontab
crontab -e

# Add these lines:
0 2 * * 0 /Users/sondosahmed/Documents/ALX/alx-backend-graphql_crm/crm/cron_jobs/clean_inactive_customers.sh
0 8 * * * /Users/sondosahmed/Documents/ALX/alx-backend-graphql_crm/crm/cron_jobs/send_order_reminders.py
```

### 4. Add Django-crontab jobs
```bash
# Add django-crontab jobs
python3 manage.py crontab add

# View configured django-crontab jobs
python3 manage.py crontab show

# Remove django-crontab jobs (if needed)
python3 manage.py crontab remove
```

### 5. Verify the cron jobs
```bash
crontab -l
```

## Manual Execution

You can run the scripts manually for testing:

```bash
# Test customer cleanup
./crm/cron_jobs/clean_inactive_customers.sh

# Test order reminders
python3 crm/cron_jobs/send_order_reminders.py

# Test heartbeat logger
python3 manage.py shell -c "from crm.cron import log_crm_heartbeat; log_crm_heartbeat()"
```

## Logging

### Customer Cleanup Log
```
Sat Aug 30 13:01:52 EEST 2025: Starting customer cleanup script
Sat Aug 30 13:01:53 EEST 2025: Customer cleanup script completed successfully
Sat Aug 30 13:01:53 EEST 2025: Check the output above for details on deleted customers
Sat Aug 30 13:01:53 EEST 2025: Customer cleanup script finished
----------------------------------------
```

### Order Reminders Log
```
2025-08-30 10:15:08 - INFO - Starting Order Reminders Script
2025-08-30 10:15:08 - INFO - Setting up GraphQL client...
2025-08-30 10:15:08 - INFO - GraphQL client setup successful
2025-08-30 10:15:08 - INFO - Querying for orders from the last 7 days...
2025-08-30 10:15:08 - INFO - Successfully queried GraphQL endpoint for orders since 2025-08-23
2025-08-30 10:15:08 - INFO - Processing 1 orders...
2025-08-30 10:15:08 - INFO - ORDER REMINDER - Order ID: T3JkZXJUeXBlOjg=, Customer: Requirement Test User (requirement@example.com), Date: 2025-08-17T18:13:47.790650+00:00, Total: $199.99, Products: Low Stock Product
2025-08-30 10:15:08 - INFO - Order reminders processing completed. Processed 1 orders.
```

### Heartbeat Log
```
30/08/2025-10:16:14 CRM is alive
30/08/2025-10:16:14 GraphQL endpoint responsive: 7 customers found
30/08/2025-10:17:05 CRM is alive
30/08/2025-10:17:05 GraphQL endpoint responsive: 7 customers found
```

## Safety Features

- **Transaction Safety**: Uses Django transactions for data consistency
- **Error Handling**: Continues processing even if individual operations fail
- **Validation**: Checks project directory and Django installation before execution
- **Logging**: Comprehensive logging of all operations and errors
- **Exit Codes**: Proper exit codes for cron job monitoring
- **GraphQL Health Checks**: Verifies GraphQL endpoint responsiveness

## Cron Schedule Format

### Customer Cleanup
- **`0 2 * * 0`** - Every Sunday at 2:00 AM

### Order Reminders
- **`0 8 * * *`** - Every day at 8:00 AM

### Heartbeat Logger
- **`*/5 * * * *`** - Every 5 minutes

### Stock Updates
- **`0 */12 * * *`** - Every 12 hours

## Monitoring

To monitor if the cron jobs are running:

1. **Check the log files**:
   ```bash
   tail -f /tmp/customer_cleanup_log.txt
   tail -f /tmp/order_reminders_log.txt
   tail -f /tmp/crm_heartbeat_log.txt
   ```

2. **Check system cron logs**:
   ```bash
   grep "customer_cleanup\|order_reminders" /var/log/cron.log
   ```

3. **Check django-crontab status**:
   ```bash
   python3 manage.py crontab show
   ```

4. **Verify data changes**:
   ```bash
   python3 manage.py shell -c "from crm.models import Customer, Order; print(f'Customers: {Customer.objects.count()}, Orders: {Order.objects.count()}')"
   ```

## Troubleshooting

### Common Issues

1. **Permission Denied**: Make sure scripts are executable
   ```bash
   chmod +x crm/cron_jobs/clean_inactive_customers.sh
   ```

2. **Path Issues**: Verify the full paths in crontab entries

3. **Django Not Found**: Ensure Django is installed and accessible

4. **GraphQL Connection Issues**: Check if Django server is running

5. **Log File Issues**: Check if `/tmp` directory is writable

6. **Django-Crontab Issues**: 
   ```bash
   # Reinstall django-crontab jobs
   python3 manage.py crontab remove
   python3 manage.py crontab add
   ```

### Testing the Scripts

Before adding to crontab, test manually:
```bash
cd /Users/sondosahmed/Documents/ALX/alx-backend-graphql_crm

# Test customer cleanup
./crm/cron_jobs/clean_inactive_customers.sh

# Test order reminders
python3 crm/cron_jobs/send_order_reminders.py

# Test heartbeat
python3 manage.py shell -c "from crm.cron import log_crm_heartbeat; log_crm_heartbeat()"
```

## Customization

To modify the scripts:

1. **Change cleanup criteria**: Modify the `timedelta(days=365)` in customer cleanup
2. **Change reminder period**: Modify the `DAYS_LOOKBACK` in order reminders
3. **Change heartbeat interval**: Update the cron schedule in settings.py
4. **Change logging location**: Update the `LOG_FILE` variables
5. **Add more conditions**: Modify the filtering logic in each script

## Dependencies

- **Django**: Web framework
- **django-crontab**: Cron job management
- **gql**: GraphQL client library
- **requests**: HTTP library for GraphQL queries
- **django-filters**: Filtering capabilities
- **graphene-django**: GraphQL integration
