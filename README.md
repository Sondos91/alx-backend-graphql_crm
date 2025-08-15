# ALX Backend GraphQL CRM

A Django-based CRM system with GraphQL API endpoints, built for the ALX Backend Specialization program.

## 🚀 Features

- **Django 5.2.4** - Modern web framework
- **GraphQL API** - Flexible data querying with graphene-django
- **CRM App** - Customer Relationship Management functionality
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

### 4. Start the Development Server
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

### Current Schema

The project includes a basic GraphQL schema with a simple query:

```graphql
type Query {
  hello: String!
}
```

### Example Query

```graphql
{
  hello
}
```

**Response:**
```json
{
  "data": {
    "hello": "Hello, GraphQL!"
  }
}
```

## 📁 Project Structure

```
alx-backend-graphql_crm/
├── alx_backend_graphql_crm/          # Main project directory
│   ├── __init__.py
│   ├── settings.py                   # Django settings & GraphQL config
│   ├── urls.py                       # URL routing with GraphQL endpoint
│   ├── wsgi.py                       # WSGI application entry point
│   ├── asgi.py                       # ASGI application entry point
│   └── schema.py                     # GraphQL schema definition
├── crm/                              # CRM application
│   ├── __init__.py
│   ├── admin.py                      # Django admin configuration
│   ├── apps.py                       # App configuration
│   ├── models.py                     # Database models
│   ├── views.py                      # View functions
│   ├── tests.py                      # Test cases
│   └── migrations/                   # Database migrations
├── manage.py                         # Django management script
├── requirements.txt                  # Python dependencies
├── db.sqlite3                        # SQLite database
└── README.md                         # This file
```

## ⚙️ Configuration

### Django Settings (`settings.py`)

Key configurations include:
- **INSTALLED_APPS**: Added `graphene_django` and `crm`
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

1. **Define the type** in `schema.py`:
```python
class User(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    email = graphene.String()
```

2. **Add to Query class**:
```python
class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")
    users = graphene.List(User)
    
    def resolve_users(self, info):
        # Return list of users
        return []
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

### Server Logs

The development server provides detailed logs. Common log entries:
- `"GET /graphql HTTP/1.1" 400` - Bad request (expected for GET without query)
- `"POST /graphql HTTP/1.1" 200` - Successful GraphQL query

## 🚀 Next Steps

1. **Add Models**: Create Django models in `crm/models.py`
2. **Extend Schema**: Add more GraphQL types and queries
3. **Authentication**: Implement user authentication and authorization
4. **Business Logic**: Add CRM-specific functionality
5. **Testing**: Write comprehensive test cases
6. **Production**: Configure for production deployment

## 📞 Support

For issues and questions:
- Check Django documentation: https://docs.djangoproject.com/
- GraphQL documentation: https://graphql.org/
- graphene-django docs: https://docs.graphene-python.org/projects/django/

## 📄 License

This project is part of the ALX Backend Specialization program.

---

**Happy Coding! 🎉**
