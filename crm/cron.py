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


def update_low_stock():
    """
    Update low-stock products (stock < 10) by incrementing their stock by 10.
    This function is called by django-crontab every 12 hours.
    """
    try:
        # Get current timestamp in the required format DD/MM/YYYY-HH:MM:SS
        current_time = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
        
        # Log file path
        log_file = "/tmp/low_stock_updates_log.txt"
        
        # Setup Django environment for GraphQL mutation
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')
        django.setup()
        
        try:
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
            
            # Execute the UpdateLowStockProducts mutation
            mutation = gql("""
            mutation {
                updateLowStockProducts {
                    success
                    message
                    updatedCount
                    updatedProducts {
                        id
                        name
                        stock
                        price
                    }
                }
            }
            """)
            
            # Execute mutation
            result = client.execute(mutation)
            mutation_result = result.get('updateLowStockProducts', {})
            
            # Log the results
            success = mutation_result.get('success', False)
            message = mutation_result.get('message', 'No message')
            updated_count = mutation_result.get('updatedCount', 0)
            updated_products = mutation_result.get('updatedProducts', [])
            
            # Log to file
            with open(log_file, 'a') as f:
                f.write(f"{current_time} - Stock Update Job Started\n")
                f.write(f"{current_time} - Success: {success}\n")
                f.write(f"{current_time} - Message: {message}\n")
                f.write(f"{current_time} - Updated Count: {updated_count}\n")
                
                if updated_products:
                    f.write(f"{current_time} - Updated Products:\n")
                    for product in updated_products:
                        product_name = product.get('name', 'Unknown')
                        new_stock = product.get('stock', 0)
                        product_id = product.get('id', 'Unknown')
                        f.write(f"{current_time} -   Product: {product_name} (ID: {product_id}), New Stock: {new_stock}\n")
                else:
                    f.write(f"{current_time} - No products were updated\n")
                
                f.write(f"{current_time} - Stock Update Job Completed\n")
                f.write("-" * 50 + "\n")
            
            # Print success message
            print(f"Stock update job completed: {message}")
            print(f"Updated {updated_count} products")
            
        except Exception as graphql_error:
            # Log GraphQL mutation failure
            error_message = f"{current_time} GraphQL mutation failed: {str(graphql_error)}"
            with open(log_file, 'a') as f:
                f.write(f"{error_message}\n")
                f.write(f"{current_time} - Stock Update Job Failed\n")
                f.write("-" * 50 + "\n")
            
            print(f"Stock update job failed: {str(graphql_error)}")
            
    except Exception as e:
        # Log any errors that occur during the stock update job
        error_time = datetime.now().strftime('%d/%m/%Y-%H:%MM:%S')
        error_message = f"{error_time} Stock update job failed: {str(e)}"
        
        try:
            with open("/tmp/low_stock_updates_log.txt", 'a') as f:
                f.write(f"{error_message}\n")
                f.write(f"{error_time} - Stock Update Job Failed\n")
                f.write("-" * 50 + "\n")
        except:
            # If we can't even write to the log file, print to console
            print(f"CRITICAL: {error_message}")
        
        # Re-raise the exception so django-crontab knows the job failed
        raise
