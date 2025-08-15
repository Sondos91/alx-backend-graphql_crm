import graphene
from graphene_django import DjangoObjectType
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .models import Customer, Product, Order, OrderItem
from decimal import Decimal


# GraphQL Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = '__all__'


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = '__all__'


class OrderItemType(DjangoObjectType):
    subtotal = graphene.Decimal()

    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = '__all__'


# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()


# Response Types
class CreateCustomerResponse(graphene.ObjectType):
    customer = graphene.Field(CustomerType)
    message = graphene.String()
    success = graphene.Boolean()


class BulkCreateCustomersResponse(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)
    success_count = graphene.Int()
    error_count = graphene.Int()


class CreateProductResponse(graphene.ObjectType):
    product = graphene.Field(ProductType)
    message = graphene.String()
    success = graphene.Boolean()


class CreateOrderResponse(graphene.ObjectType):
    order = graphene.Field(OrderType)
    message = graphene.String()
    success = graphene.Boolean()


# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    Output = CreateCustomerResponse

    def mutate(self, info, input):
        try:
            # Validate email uniqueness
            if Customer.objects.filter(email=input.email).exists():
                return CreateCustomerResponse(
                    customer=None,
                    message="Email already exists",
                    success=False
                )

            # Validate phone format if provided
            if input.phone:
                import re
                phone_pattern = r'^[\+]?[1-9][\d]{0,15}$'
                if not re.match(phone_pattern, input.phone):
                    return CreateCustomerResponse(
                        customer=None,
                        message="Phone number must contain only digits and optionally start with +",
                        success=False
                    )

            customer = Customer.objects.create(
                name=input.name,
                email=input.email,
                phone=input.phone
            )

            return CreateCustomerResponse(
                customer=customer,
                message="Customer created successfully",
                success=True
            )

        except Exception as e:
            return CreateCustomerResponse(
                customer=None,
                message=f"Error creating customer: {str(e)}",
                success=False
            )


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    Output = BulkCreateCustomersResponse

    def mutate(self, info, input):
        customers = []
        errors = []
        success_count = 0
        error_count = 0

        with transaction.atomic():
            for customer_data in input:
                try:
                    # Check if email already exists
                    if Customer.objects.filter(email=customer_data.email).exists():
                        errors.append(f"Email {customer_data.email} already exists")
                        error_count += 1
                        continue

                    # Validate phone format if provided
                    if customer_data.phone:
                        import re
                        phone_pattern = r'^[\+]?[1-9][\d]{0,15}$'
                        if not re.match(phone_pattern, customer_data.phone):
                            errors.append(f"Invalid phone format for {customer_data.email}")
                            error_count += 1
                            continue

                    customer = Customer.objects.create(
                        name=customer_data.name,
                        email=customer_data.email,
                        phone=customer_data.phone
                    )
                    customers.append(customer)
                    success_count += 1

                except Exception as e:
                    errors.append(f"Error creating {customer_data.email}: {str(e)}")
                    error_count += 1

        return BulkCreateCustomersResponse(
            customers=customers,
            errors=errors,
            success_count=success_count,
            error_count=error_count
        )


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    Output = CreateProductResponse

    def mutate(self, info, input):
        try:
            # Validate price is positive
            if input.price <= 0:
                return CreateProductResponse(
                    product=None,
                    message="Price must be greater than 0",
                    success=False
                )

            # Validate stock is non-negative
            stock = input.stock if input.stock is not None else 0
            if stock < 0:
                return CreateProductResponse(
                    product=None,
                    message="Stock cannot be negative",
                    success=False
                )

            product = Product.objects.create(
                name=input.name,
                price=input.price,
                stock=stock
            )

            return CreateProductResponse(
                product=product,
                message="Product created successfully",
                success=True
            )

        except Exception as e:
            return CreateProductResponse(
                product=None,
                message=f"Error creating product: {str(e)}",
                success=False
            )


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    Output = CreateOrderResponse

    def mutate(self, info, input):
        try:
            # Validate customer exists
            try:
                customer = Customer.objects.get(id=input.customer_id)
            except Customer.DoesNotExist:
                return CreateOrderResponse(
                    order=None,
                    message="Customer not found",
                    success=False
                )

            # Validate at least one product
            if not input.product_ids:
                return CreateOrderResponse(
                    order=None,
                    message="At least one product must be selected",
                    success=False
                )

            # Validate products exist and get their prices
            products = []
            total_amount = Decimal('0.00')
            
            for product_id in input.product_ids:
                try:
                    product = Product.objects.get(id=product_id)
                    products.append(product)
                    total_amount += product.price
                except Product.DoesNotExist:
                    return CreateOrderResponse(
                        order=None,
                        message=f"Product with ID {product_id} not found",
                        success=False
                    )

            with transaction.atomic():
                # Create order
                order = Order.objects.create(
                    customer=customer,
                    total_amount=total_amount
                )

                # Create order items
                for product in products:
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        price_at_time=product.price
                    )

            return CreateOrderResponse(
                order=order,
                message="Order created successfully",
                success=True
            )

        except Exception as e:
            return CreateOrderResponse(
                order=None,
                message=f"Error creating order: {str(e)}",
                success=False
            )


# Queries
class Query(graphene.ObjectType):
    # Customer queries
    all_customers = graphene.List(CustomerType)
    customer = graphene.Field(CustomerType, id=graphene.ID(required=True))
    
    # Product queries
    all_products = graphene.List(ProductType)
    product = graphene.Field(ProductType, id=graphene.ID(required=True))
    
    # Order queries
    all_orders = graphene.List(OrderType)
    order = graphene.Field(OrderType, id=graphene.ID(required=True))
    customer_orders = graphene.List(OrderType, customer_id=graphene.ID(required=True))

    def resolve_all_customers(self, info):
        return Customer.objects.all()

    def resolve_customer(self, info, id):
        try:
            return Customer.objects.get(id=id)
        except Customer.DoesNotExist:
            return None

    def resolve_all_products(self, info):
        return Product.objects.all()

    def resolve_product(self, info, id):
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            return None

    def resolve_all_orders(self, info):
        return Order.objects.all()

    def resolve_order(self, info, id):
        try:
            return Order.objects.get(id=id)
        except Order.DoesNotExist:
            return None

    def resolve_customer_orders(self, info, customer_id):
        try:
            customer = Customer.objects.get(id=customer_id)
            return customer.orders.all()
        except Customer.DoesNotExist:
            return []


# Mutations
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
