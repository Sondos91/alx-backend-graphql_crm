# ALX Backend GraphQL CRM

A Django-based CRM system with GraphQL API endpoints, built for the ALX Backend Specialization program. This project implements advanced GraphQL mutations for customer, product, and order management, along with comprehensive filtering and search capabilities.

## 🚀 Features

- **Django 5.2.4** - Modern web framework
- **GraphQL API** - Flexible data querying with graphene-django
- **CRM App** - Customer Relationship Management functionality
- **Advanced Mutations** - Create, update, and manage CRM entities
- **Comprehensive Filtering** - Search and filter customers, products, and orders
- **Bulk Operations** - Handle multiple records with transaction safety
- **SQLite Database** - Lightweight database for development
- **GraphiQL Interface** - Interactive GraphQL playground

## 📋 Prerequisites

- Python 3.8+
- pip (Python package installer)
- Git

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd alx-backend-graphql_crm
```

### 2. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 3. Run Database Migrations
```bash
python3 manage.py migrate
```

### 4. Seed the Database (Optional)
```bash
python3 seed_db.py
```

### 5. Start the Development Server
```bash
python3 manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`

## 🌐 GraphQL Endpoint

### Access GraphiQL Interface
Visit: `http://localhost:8000/graphql`

This provides an interactive GraphQL playground where you can:
- Write and test queries
- Explore the schema
- View documentation
- Execute mutations

## 📊 Data Models

### Customer Model
- **name** (required): Customer's full name
- **email** (required, unique): Customer's email address
- **phone** (optional): Phone number with validation
- **created_at**: Timestamp of creation
- **updated_at**: Timestamp of last update

### Product Model
- **name** (required): Product name
- **price** (required): Product price (must be positive)
- **stock** (optional): Available stock quantity (default: 0)
- **created_at**: Timestamp of creation
- **updated_at**: Timestamp of last update

### Order Model
- **customer** (required): Reference to customer
- **products** (required): Many-to-many relationship with products
- **total_amount**: Calculated total of order
- **order_date**: When the order was placed
- **created_at**: Timestamp of creation
- **updated_at**: Timestamp of last update

### OrderItem Model
- **order**: Reference to order
- **product**: Reference to product
- **quantity**: Quantity ordered
- **price_at_time**: Price when order was placed
- **subtotal**: Calculated subtotal (quantity × price)

## 🔧 GraphQL Mutations (Task 2)

### CreateCustomer
Creates a single customer with validation.

```graphql
mutation {
  createCustomer(input: {
    name: "John Doe"
    email: "john@example.com"
    phone: "+1234567890"
  }) {
    customer {
      id
      name
      email
      phone
    }
    message
    success
  }
}
```

**Features:**
- ✅ Email uniqueness validation
- ✅ Phone format validation
- ✅ Returns created customer + success message
- ✅ Comprehensive error handling

### BulkCreateCustomers
Creates multiple customers in a single transaction.

```graphql
mutation {
  bulkCreateCustomers(input: [
    { name: "Alice", email: "alice@example.com", phone: "1234567890" },
    { name: "Bob", email: "bob@example.com", phone: "9876543210" }
  ]) {
    customers {
      id
      name
      email
      phone
    }
    errors
    successCount
    errorCount
  }
}
```

**Features:**
- ✅ Transaction safety with atomic operations
- ✅ Partial success support (valid customers created even if some fail)
- ✅ Detailed error reporting for each failed record
- ✅ Success and error counts

### CreateProduct
Creates a product with validation.

```graphql
mutation {
  createProduct(input: {
    name: "Laptop Pro"
    price: "1299.99"
    stock: 15
  }) {
    product {
      id
      name
      price
      stock
    }
    message
    success
  }
}
```

**Features:**
- ✅ Price validation (must be positive)
- ✅ Stock validation (must be non-negative)
- ✅ Returns created product + success message

### CreateOrder
Creates an order with product associations.

```graphql
mutation {
  createOrder(input: {
    customerId: "1"
    productIds: ["1", "2", "3"]
  }) {
    order {
      id
      customer {
        name
        email
      }
      products {
        name
        price
      }
      totalAmount
      orderDate
    }
    message
    success
  }
}
```

**Features:**
- ✅ Customer existence validation
- ✅ Product existence validation
- ✅ Automatic total calculation
- ✅ Product association through OrderItem
- ✅ Price preservation at order time

## 🔍 GraphQL Queries & Filtering (Task 3)

### Basic Queries
```graphql
# Get all customers
query {
  allCustomers {
    edges {
      node {
        id
        name
        email
        phone
        createdAt
      }
    }
  }
}

# Get all products
query {
  allProducts {
    edges {
      node {
        id
        name
        price
        stock
      }
    }
  }
}

# Get all orders
query {
  allOrders {
    edges {
      node {
        id
        customer {
          name
        }
        totalAmount
        orderDate
      }
    }
  }
}
```

### Advanced Filtering

#### Customer Filtering
```graphql
query {
  filteredCustomers(
    nameIcontains: "Ali"
    emailIcontains: "example"
    createdAtGte: "2025-01-01"
    phonePattern: "+1"
    orderBy: "name"
  ) {
    id
    name
    email
    phone
    createdAt
  }
}
```

**Available Filters:**
- `nameIcontains`: Case-insensitive name search
- `emailIcontains`: Case-insensitive email search
- `createdAtGte`: Created after date
- `createdAtLte`: Created before date
- `phonePattern`: Phone numbers starting with pattern
- `orderBy`: Sort by field (e.g., "name", "-createdAt")

#### Product Filtering
```graphql
query {
  filteredProducts(
    nameIcontains: "Laptop"
    priceGte: "100"
    priceLte: "2000"
    stockGte: "10"
    lowStock: true
    orderBy: "-price"
  ) {
    id
    name
    price
    stock
  }
}
```

**Available Filters:**
- `nameIcontains`: Case-insensitive name search
- `priceGte`: Price greater than or equal to
- `priceLte`: Price less than or equal to
- `stockGte`: Stock greater than or equal to
- `stockLte`: Stock less than or equal to
- `lowStock`: Products with stock < 10
- `orderBy`: Sort by field (e.g., "price", "-stock")

#### Order Filtering
```graphql
query {
  filteredOrders(
    totalAmountGte: "500"
    customerName: "Alice"
    productName: "Laptop"
    orderDateGte: "2025-01-01"
    orderBy: "-orderDate"
  ) {
    id
    customer {
      name
      email
    }
    totalAmount
    orderDate
  }
}
```

**Available Filters:**
- `totalAmountGte`: Total amount greater than or equal to
- `totalAmountLte`: Total amount less than or equal to
- `orderDateGte`: Order date after
- `orderDateLte`: Order date before
- `customerName`: Filter by customer name
- `productName`: Filter by product name
- `productId`: Filter by specific product ID
- `orderBy`: Sort by field (e.g., "totalAmount", "-orderDate")

## ⚙️ Configuration

### Django Settings (`settings.py`)

Key configurations include:
- **INSTALLED_APPS**: Added `graphene_django`, `django_filters`, and `crm`
- **GRAPHENE**: Configured to use the main schema
- **Database**: SQLite for development
- **Debug**: Enabled for development

### URL Configuration (`urls.py`)

GraphQL endpoint is configured at `/graphql` with:
- CSRF exemption for testing
- GraphiQL interface enabled
- Proper import of GraphQLView

## 🔧 Development

### Adding New GraphQL Types

1. **Define the type** in `crm/schema.py`:
```python
class NewType(DjangoObjectType):
    class Meta:
        model = NewModel
        fields = '__all__'
        filterset_class = NewFilter
        interfaces = (graphene.relay.Node,)
```

2. **Add to Query class**:
```python
class Query(graphene.ObjectType):
    all_new_types = DjangoFilterConnectionField(NewType)
    filtered_new_types = graphene.List(NewType, ...)
```

### Adding New Filters

1. **Create filter class** in `crm/filters.py`:
```python
class NewFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = NewModel
        fields = ['name']
```

2. **Add custom filter methods**:
```python
def filter_custom_field(self, queryset, name, value):
    if value:
        return queryset.filter(custom_field__contains=value)
    return queryset
```

### Running Tests
```bash
python3 manage.py test
```

### Creating Migrations
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

## 📚 Dependencies

- **Django** >= 5.2.4 - Web framework
- **graphene-django** >= 3.2.3 - GraphQL integration
- **django-filter** >= 25.1 - Filtering capabilities

## 🚨 Important Notes

- **Development Server**: This is a development setup. Do not use in production.
- **CSRF**: CSRF protection is disabled for the GraphQL endpoint for testing purposes.
- **Database**: Uses SQLite by default. Configure PostgreSQL/MySQL for production.
- **Filtering**: Advanced filtering supports case-insensitive searches and range queries.
- **Mutations**: All mutations include comprehensive validation and error handling.

## 🔍 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Kill existing Django processes
   pkill -f "python3 manage.py runserver"
   ```

2. **Import Errors**
   - Ensure all dependencies are installed: `pip3 install -r requirements.txt`
   - Check Python path and virtual environment

3. **Database Errors**
   - Run migrations: `python3 manage.py migrate`
   - Check database file permissions

4. **Filter Issues**
   - Verify filter parameters match the schema
   - Check date format for date filters (YYYY-MM-DD)
   - Ensure decimal values are passed as strings

### Server Logs

The development server provides detailed logs. Common log entries:
- `"GET /graphql HTTP/1.1" 400` - Bad request (expected for GET without query)
- `"POST /graphql HTTP/1.1" 200` - Successful GraphQL query/mutation
- `"POST /graphql HTTP/1.1" 400` - GraphQL validation error

## 🚀 Next Steps

1. **Authentication**: Implement user authentication and authorization
2. **Pagination**: Add pagination support for large result sets
3. **Caching**: Implement Redis caching for improved performance
4. **Testing**: Write comprehensive test cases for all mutations and filters
5. **Production**: Configure for production deployment with PostgreSQL
6. **API Documentation**: Generate OpenAPI/Swagger documentation
7. **Rate Limiting**: Add rate limiting for API endpoints
8. **Monitoring**: Implement logging and monitoring

## 📞 Support

For issues and questions:
- Check Django documentation: https://docs.djangoproject.com/
- GraphQL documentation: https://graphql.org/
- graphene-django docs: https://docs.graphene-python.org/projects/django/
- django-filter docs: https://django-filter.readthedocs.io/

## 📄 License

This project is part of the ALX Backend Specialization program.

---

**Happy Coding! 🎉**

## 🎯 **Task Completion Status**

- ✅ **Task 1**: Basic GraphQL setup and schema
- ✅ **Task 2**: Complex GraphQL mutations with validation and error handling
- ✅ **Task 3**: Advanced filtering and search capabilities
- 🚧 **Future**: Authentication, pagination, and production deployment
