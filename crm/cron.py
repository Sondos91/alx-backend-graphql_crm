"""
Cron jobs for ALX Backend GraphQL CRM
This module contains scheduled tasks that run via django-crontab
"""

import os
import sys
import django
from datetime import datetime
from django.utils import timezone
import logging

# Setup logging for the cron job
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_crm_heartbeat():
    """
    Log a heartbeat message every 5 minutes to confirm CRM application health.
    This function is called by django-crontab every 5 minutes.
    """
    try:
        # Get current timestamp in the required format DD/MM/YYYY-HH:MM:SS
        current_time = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
        
        # Heartbeat message
        heartbeat_message = f"{current_time} CRM is alive"
        
        # Log file path
        log_file = "/tmp/crm_heartbeat_log.txt"
        
        # Append heartbeat message to log file
        with open(log_file, 'a') as f:
            f.write(f"{heartbeat_message}\n")
        
        # Optional: Query GraphQL hello field to verify endpoint responsiveness
        try:
            # Setup Django environment for GraphQL query
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')
            django.setup()
            
            # Import GraphQL client and schema
            from gql import gql, Client
            from gql.transport.requests import RequestsHTTPTransport
            
            # Setup GraphQL client
            transport = RequestsHTTPTransport(
                url="http://localhost:8000/graphql",
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            client = Client(transport=transport, fetch_schema_from_transport=True)
            
            # Query for a simple field that exists in our schema
            query = gql("""
            query {
                allCustomers {
                    edges {
                        node {
                            id
                        }
                    }
                }
            }
            """)
            
            # Execute query
            result = client.execute(query)
            customer_count = len(result.get('allCustomers', {}).get('edges', []))
            
            # Log GraphQL health check
            graphql_status = f"GraphQL endpoint responsive: {customer_count} customers found"
            with open(log_file, 'a') as f:
                f.write(f"{current_time} {graphql_status}\n")
                
        except Exception as graphql_error:
            # Log GraphQL check failure but don't fail the entire heartbeat
            error_message = f"{current_time} GraphQL health check failed: {str(graphql_error)}"
            with open(log_file, 'a') as f:
                f.write(f"{error_message}\n")
        
        # Log successful heartbeat
        print(f"Heartbeat logged successfully: {heartbeat_message}")
        
    except Exception as e:
        # Log any errors that occur during heartbeat logging
        error_time = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
        error_message = f"{error_time} Heartbeat logging failed: {str(e)}"
        
        try:
            with open("/tmp/crm_heartbeat_log.txt", 'a') as f:
                f.write(f"{error_message}\n")
        except:
            # If we can't even write to the log file, print to console
            print(f"CRITICAL: {error_message}")
        
        # Re-raise the exception so django-crontab knows the job failed
        raise
