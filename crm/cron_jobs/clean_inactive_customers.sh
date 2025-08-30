#!/bin/bash

# Customer Cleanup Script for ALX Backend GraphQL CRM
# This script deletes customers with no orders since a year ago
# Run via cron job every Sunday at 2:00 AM

# Set the project directory
PROJECT_DIR="/Users/sondosahmed/Documents/ALX/alx-backend-graphql_crm"
LOG_FILE="/tmp/customer_cleanup_log.txt"

# Function to log messages with timestamp
log_message() {
    echo "$(date): $1" >> "$LOG_FILE"
}

# Function to log errors
log_error() {
    echo "$(date): ERROR - $1" >> "$LOG_FILE"
}

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    log_error "Project directory $PROJECT_DIR does not exist"
    exit 1
fi

# Change to project directory
cd "$PROJECT_DIR" || {
    log_error "Could not change to project directory $PROJECT_DIR"
    exit 1
}

# Check if manage.py exists
if [ ! -f "manage.py" ]; then
    log_error "manage.py not found in project directory"
    exit 1
fi

# Check if Django is properly installed
if ! python3 -c "import django" 2>/dev/null; then
    log_error "Django is not installed or not accessible"
    exit 1
fi

# Log script execution start
log_message "Starting customer cleanup script"

# Execute Django management command to clean up inactive customers
python3 manage.py shell << 'EOF'
import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')
django.setup()

from crm.models import Customer, Order

try:
    # Calculate the cutoff date (1 year ago)
    cutoff_date = timezone.now() - timedelta(days=365)
    
    # Find customers with no orders since the cutoff date
    customers_to_delete = []
    
    for customer in Customer.objects.all():
        # Check if customer has any orders since the cutoff date
        recent_orders = Order.objects.filter(
            customer=customer,
            order_date__gte=cutoff_date
        )
        
        if not recent_orders.exists():
            customers_to_delete.append(customer)
    
    # Delete inactive customers in a transaction
    deleted_count = 0
    with transaction.atomic():
        for customer in customers_to_delete:
            try:
                customer_name = customer.name
                customer_email = customer.email
                customer.delete()
                deleted_count += 1
                print(f"Deleted customer: {customer_name} ({customer_email})")
            except Exception as e:
                print(f"Error deleting customer {customer.name}: {str(e)}")
                # Continue with other customers even if one fails
    
    # Print summary
    print(f"Customer cleanup completed. Deleted {deleted_count} inactive customers.")
    print(f"Cutoff date: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total customers before cleanup: {Customer.objects.count() + deleted_count}")
    print(f"Total customers after cleanup: {Customer.objects.count()}")
    
except Exception as e:
    print(f"Fatal error during cleanup: {str(e)}")
    sys.exit(1)

# Exit the shell
exit()
EOF

# Capture the exit code
EXIT_CODE=$?

# Log the results
if [ $EXIT_CODE -eq 0 ]; then
    log_message "Customer cleanup script completed successfully"
    log_message "Check the output above for details on deleted customers"
else
    log_error "Customer cleanup script failed with exit code $EXIT_CODE"
fi

# Log script completion
log_message "Customer cleanup script finished"
echo "----------------------------------------" >> "$LOG_FILE"

# Exit with the same code as the Python script
exit $EXIT_CODE
