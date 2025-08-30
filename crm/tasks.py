"""
Celery tasks for ALX Backend GraphQL CRM
"""

import os
import django
import requests
from datetime import datetime
from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


@shared_task
def generate_crm_report():
    """
    Generate a weekly CRM report with total customers, orders, and revenue.
    This task is scheduled to run every Monday at 6:00 AM via Celery Beat.
    """
    try:
        # Setup Django environment
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')
        django.setup()
        
        # Setup GraphQL client
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # GraphQL query to fetch CRM data
        query = gql("""
        query {
            allCustomers {
                edges {
                    node {
                        id
                    }
                }
            }
            allOrders {
                edges {
                    node {
                        totalAmount
                    }
                }
            }
        }
        """)
        
        # Execute query
        result = client.execute(query)
        
        # Extract data
        customers = result.get('allCustomers', {}).get('edges', [])
        customer_count = len(customers)
        
        orders = result.get('allOrders', {}).get('edges', [])
        order_count = len(orders)
        
        # Calculate total revenue
        total_revenue = sum(
            float(order['node']['totalAmount']) 
            for order in orders 
            if order['node']['totalAmount']
        )
        
        # Format timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create report message
        report_message = f"{timestamp} - Report: {customer_count} customers, {order_count} orders, ${total_revenue:.2f} revenue"
        
        # Log to file
        log_file = "/tmp/crm_report_log.txt"
        with open(log_file, 'a') as f:
            f.write(f"{report_message}\n")
            f.write("-" * 60 + "\n")
        
        print(f"CRM Report generated successfully: {report_message}")
        return {
            'success': True,
            'customers': customer_count,
            'orders': order_count,
            'revenue': total_revenue,
            'timestamp': timestamp
        }
        
    except Exception as e:
        error_message = f"Error generating CRM report: {str(e)}"
        print(error_message)
        
        # Log error to file
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_file = "/tmp/crm_report_log.txt"
        with open(log_file, 'a') as f:
            f.write(f"{timestamp} - ERROR: {error_message}\n")
            f.write("-" * 60 + "\n")
        
        return {
            'success': False,
            'error': str(e),
            'timestamp': timestamp
        }
