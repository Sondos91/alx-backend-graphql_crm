#!/usr/bin/env python3
"""
Order Reminders Script for ALX Backend GraphQL CRM
This script queries the GraphQL endpoint for orders from the last 7 days
and logs reminders for each order found.

Run via cron job daily at 8:00 AM
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Configuration
GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"
LOG_FILE = "/tmp/order_reminders_log.txt"
DAYS_LOOKBACK = 7

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def setup_gql_client():
    """Setup GraphQL client with proper transport"""
    try:
        transport = RequestsHTTPTransport(
            url=GRAPHQL_ENDPOINT,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        return client
    except Exception as e:
        logger.error(f"Failed to setup GraphQL client: {str(e)}")
        return None

def get_recent_orders(client):
    """Query GraphQL for orders from the last 7 days"""
    try:
        # Calculate the cutoff date (7 days ago)
        cutoff_date = (datetime.now() - timedelta(days=DAYS_LOOKBACK)).strftime('%Y-%m-%d')
        
        # GraphQL query to get orders from the last 7 days
        query = gql("""
        query GetRecentOrders($cutoffDate: String!) {
            filteredOrders(orderDateGte: $cutoffDate) {
                id
                orderDate
                totalAmount
                customer {
                    id
                    name
                    email
                }
                products {
                    id
                    name
                    price
                }
            }
        }
        """)
        
        variables = {"cutoffDate": cutoff_date}
        
        # Execute the query
        result = client.execute(query, variable_values=variables)
        
        logger.info(f"Successfully queried GraphQL endpoint for orders since {cutoff_date}")
        return result.get('filteredOrders', [])
        
    except Exception as e:
        logger.error(f"Failed to query GraphQL: {str(e)}")
        return []

def process_order_reminders(orders):
    """Process orders and log reminders"""
    if not orders:
        logger.info("No recent orders found to process")
        return 0
    
    processed_count = 0
    
    for order in orders:
        try:
            order_id = order.get('id', 'Unknown')
            customer_name = order.get('customer', {}).get('name', 'Unknown Customer')
            customer_email = order.get('customer', {}).get('email', 'No Email')
            order_date = order.get('orderDate', 'Unknown Date')
            total_amount = order.get('totalAmount', '0.00')
            
            # Get product details
            products = order.get('products', [])
            product_names = [p.get('name', 'Unknown Product') for p in products]
            
            # Log the reminder
            reminder_message = (
                f"ORDER REMINDER - Order ID: {order_id}, "
                f"Customer: {customer_name} ({customer_email}), "
                f"Date: {order_date}, "
                f"Total: ${total_amount}, "
                f"Products: {', '.join(product_names)}"
            )
            
            logger.info(reminder_message)
            processed_count += 1
            
        except Exception as e:
            logger.error(f"Error processing order {order.get('id', 'Unknown')}: {str(e)}")
            continue
    
    return processed_count

def main():
    """Main function to execute the order reminder script"""
    logger.info("=" * 60)
    logger.info("Starting Order Reminders Script")
    logger.info("=" * 60)
    
    try:
        # Setup GraphQL client
        logger.info("Setting up GraphQL client...")
        client = setup_gql_client()
        
        if not client:
            logger.error("Failed to setup GraphQL client. Exiting.")
            sys.exit(1)
        
        logger.info("GraphQL client setup successful")
        
        # Query for recent orders
        logger.info(f"Querying for orders from the last {DAYS_LOOKBACK} days...")
        orders = get_recent_orders(client)
        
        if not orders:
            logger.info("No orders found in the specified time period")
            print("Order reminders processed!")
            return
        
        # Process order reminders
        logger.info(f"Processing {len(orders)} orders...")
        processed_count = process_order_reminders(orders)
        
        # Log summary
        logger.info(f"Order reminders processing completed. Processed {processed_count} orders.")
        logger.info("=" * 60)
        
        # Print success message to console
        print("Order reminders processed!")
        
    except Exception as e:
        error_msg = f"Fatal error in order reminders script: {str(e)}"
        logger.error(error_msg)
        print(f"ERROR: {error_msg}")
        sys.exit(1)

if __name__ == "__main__":
    main()
