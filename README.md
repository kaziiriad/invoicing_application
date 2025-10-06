# InvoiceFlow - Complete Invoicing Management System

This project implements a comprehensive full-stack invoicing management system consisting of a robust Django REST Framework backend and a modern React frontend. The system provides complete invoice lifecycle management, from creation to payment, with integrated inventory tracking and user authentication.

## Project Structure

```
invoicing_application/
├── backend/                 # Django REST Framework API
│   ├── config/             # Django settings and main URLs
│   ├── invoicing/          # Core invoicing app
│   ├── users/              # User management and authentication
│   └── manage.py
├── frontend/               # React TypeScript frontend (fully implemented)
├── docker-compose.yml      # Production deployment
├── Dockerfile             # Backend container
├── Frontend_Requirements.md # Comprehensive frontend specifications
└── README.md              # This file
```

## Features

### Backend API Features
*   **Invoice Management:** Complete CRUD operations for invoices with status management (pending → paid/cancelled)
*   **Item & Inventory:** Product catalog with real-time stock tracking (on-hand, allocated, available)
*   **Transaction Tracking:** Automatic financial transaction recording for sales and payments
*   **Stock Allocation:** Advanced stock reservation system preventing overselling
*   **User Authentication:** JWT-based authentication with registration, login, logout, and token refresh
*   **API Documentation:** Interactive Swagger UI and ReDoc documentation
*   **Business Logic:** Automated calculations, validation, and status transitions

### Frontend Features (React TypeScript)
*   **User Authentication:** Login/Registration forms with JWT token management
*   **Dashboard:** Overview of invoice statistics and recent activity
*   **Invoice Management:** 
    - Create invoices with customer details and line items
    - List view with filtering, sorting, and pagination
    - Detailed invoice view with transaction history
    - Edit pending invoices
    - One-click payment processing
    - Invoice cancellation with stock release
*   **Responsive Design:** Mobile-first approach with modern UI components
*   **Real-time Calculations:** Dynamic totals and inventory updates
*   **Error Handling:** Comprehensive validation and user feedback
*   **Modern UI/UX:** Professional design with shadcn/ui components and Tailwind CSS
*   **Theme Support:** Dark/light mode toggle with system preference detection
*   **Data Visualization:** Interactive charts and analytics with Recharts

### System Features
*   **Containerized Deployment:** Production-ready Docker setup with Nginx reverse proxy
*   **Database Support:** PostgreSQL for production, SQLite for development
*   **CORS Configuration:** Ready for frontend integration
*   **Security:** JWT authentication, input validation, and secure headers

## Technologies Used

### Backend Stack
*   **Framework:** Python 3.12, Django 5.2+, Django REST Framework 3.14+
*   **Database:** PostgreSQL (production), SQLite (development)
*   **Authentication:** `djangorestframework-simplejwt` 5.3+ (JWT tokens with blacklisting)
*   **API Documentation:** `drf-yasg` 1.21+ (Swagger UI & ReDoc)
*   **Package Management:** `uv` (fast Python package manager)
*   **Web Server:** Gunicorn 21+ (production), Django dev server (development)
*   **Additional Libraries:** `django-cors-headers`, `python-dotenv`, `dj-database-url`, `psycopg[binary]`, `whitenoise`

### Frontend Stack
*   **Framework:** React 18.3.1 with TypeScript 5.8.3
*   **Build Tool:** Vite 5.4.19 with React SWC plugin
*   **UI Framework:** shadcn/ui with Radix UI primitives
*   **Styling:** Tailwind CSS 3.4.17 with custom design tokens & animations
*   **HTTP Client:** Axios 1.12.2 with TanStack React Query 5.83.0
*   **State Management:** React Context API for authentication
*   **Form Handling:** React Hook Form 7.61.1 with Zod 3.25.76 validation
*   **Routing:** React Router DOM 6.30.1
*   **Icons:** Lucide React 0.462.0 (462 icons)
*   **Date Handling:** date-fns 3.6.0 with React Day Picker 8.10.1
*   **Charts:** Recharts 2.15.4 for dashboard analytics
*   **Notifications:** Sonner 1.7.4 for toast messages
*   **Theme System:** next-themes 0.3.0 for dark/light mode
*   **Carousel:** Embla Carousel React 8.6.0
*   **Utilities:** clsx, class-variance-authority, tailwind-merge

### Deployment & DevOps
*   **Containerization:** Docker & Docker Compose
*   **Web Server:** Nginx (reverse proxy)
*   **Application Server:** Gunicorn
*   **Static Files:** WhiteNoise middleware
*   **Development:** Hot reload for both backend and frontend

## Entity-Relationship Diagram

```mermaid
erDiagram
    ITEM ||--|| INVENTORY : has
    INVOICE ||--o{ INVOICE_ITEM : contains
    INVOICE ||--o{ TRANSACTION : generates
    ITEM ||--o{ INVOICE_ITEM : included_in
    
    ITEM {
        int id PK
        string name
        text description
        int unit_price_cents
        float unit_price_cash "computed property"
    }
    
    INVENTORY {
        int id PK
        int item_id FK "REFERENCES ITEM(id)"
        int quantity_on_hand
        int quantity_allocated
        int quantity_available "computed property"
    }
    
    INVOICE {
        int id PK
        string reference_number UK "generated post_save"
        string customer_name
        string customer_email
        text customer_address
        string customer_phone
        date invoice_date
        string status "pending|paid|cancelled"
        date due_date
        int total_amount_cents "computed property"
        float total_amount_cash "computed property"
        boolean is_overdue "computed property"
    }
    
    INVOICE_ITEM {
        int id PK
        int invoice_id FK "REFERENCES INVOICE(id)"
        int item_id FK "REFERENCES ITEM(id)"
        int quantity
        int total_price_cents "computed property"
        float total_price_cash "computed property"
    }
    
    TRANSACTION {
        int id PK
        int invoice_id FK "REFERENCES INVOICE(id)"
        string transaction_type "sale|payment"
        int amount_cents
        text notes
        datetime timestamp
        float amount_cash "computed property"
    }
```

## Architecture & Design Decisions

This section explains the rationale behind the core design choices and architectural patterns used in this full-stack application.

### 1. Granular Data Models (`Item`, `Inventory`, `InvoiceItem`, `Transaction`)

*   **`Item`**: Represents a distinct product or service. Separating `Item` from `InvoiceItem` allows for a centralized product catalog. An `Item` can exist independently of any invoice and can be reused across multiple invoices.
*   **`Inventory`**: Dedicated model to track the stock levels (`quantity_on_hand`, `quantity_allocated`) for each `Item`. This separation ensures that inventory management is a distinct concern from product definition.
*   **`InvoiceItem`**: This acts as a "through" model for the Many-to-Many relationship between `Invoice` and `Item`. It's crucial for storing the `quantity` of a specific `Item` included in a particular `Invoice`. Without it, we couldn't track how many of each item were sold on a given invoice.
*   **`Transaction`**: Provides an immutable audit trail of financial events. Instead of just changing an invoice's status, explicit 'Sale' and 'Payment' transactions are recorded. This offers a more robust accounting record and historical data.

### 2. Service Layer (`InvoiceService`)

*   **Decision**: Business logic for complex operations (invoice creation, payment processing, stock management) is encapsulated within a dedicated `InvoiceService` class.
*   **Rationale**: This adheres to the Single Responsibility Principle (SRP). Serializers focus solely on data validation and formatting, while views handle HTTP request/response. The service layer orchestrates multi-step business workflows, making the code more modular, reusable, and testable.

### 3. Stock Holding Mechanism (Allocated vs. On-Hand)

*   **Decision**: Implemented a stock allocation system using `quantity_on_hand` and `quantity_allocated` fields in the `Inventory` model.
*   **Rationale**: This prevents overselling. When an invoice is created, items are "allocated" (reserved) from the `quantity_on_hand`. The `quantity_available` for new sales is `on_hand - allocated`. Only upon payment are items fully deducted from `quantity_on_hand` and released from `quantity_allocated`. This ensures stock is reserved for pending orders.

### 4. JWT Authentication

*   **Decision**: Used `djangorestframework-simplejwt` for token-based authentication.
*   **Rationale**: JWT is a standard for stateless APIs. It provides a secure way for clients to authenticate without relying on server-side sessions, making the API scalable and suitable for mobile or single-page applications.

### 5. DRF Serializer Strategy (Read/Write Separation)

*   **Decision**: Employed different serializers for different API actions (e.g., `InvoiceListSerializer`, `InvoiceDetailSerializer`, `InvoiceCreateSerializer`, `InvoiceUpdateSerializer`).
*   **Rationale**: This allows tailoring the data representation precisely for each use case. Read serializers can be optimized for display, while write serializers focus on validation and input. This keeps payloads lean and validation strict.

### 6. DRF `ModelViewSet` and Custom Actions

*   **Decision**: Utilized `ModelViewSet` for standard CRUD operations and `@action` decorator for custom endpoints like `pay` and `cancel`.
*   **Rationale**: `ModelViewSet` provides a quick and consistent way to build RESTful APIs. Custom actions allow extending the API with specific business operations that don't fit the standard CRUD model, keeping related functionality grouped within the same viewset.

### 7. `drf-yasg` for API Documentation

*   **Decision**: Integrated `drf-yasg` for automatic API documentation.
*   **Rationale**: Provides interactive Swagger UI and ReDoc interfaces directly from the codebase. This makes the API easy to explore, understand, and test for developers, significantly improving developer experience. Explicit annotations (`@swagger_auto_schema`) were added for clarity.

### 8. Docker and Docker Compose for Deployment

*   **Decision**: Containerized the application using Docker and orchestrated with Docker Compose.
*   **Rationale**: Ensures consistent development and production environments, simplifies dependency management, and provides a portable deployment unit. Gunicorn serves the Django application, and Nginx acts as a reverse proxy, serving static files and handling rate limiting.

### 9. No Saga Orchestrator Pattern

*   **Decision**: Did not implement the Saga Orchestrator pattern.
*   **Rationale**: The Saga pattern is designed for managing transactions across *distributed systems* (microservices) where a single database transaction is not possible. This project is a monolithic application with a single database. Django's `django.db.transaction.atomic()` provides full ACID (Atomicity, Consistency, Isolation, Durability) guarantees for all multi-step operations within this single database, making the complex Saga pattern unnecessary and overkill.

## Setup Instructions (Development)

Follow these steps to get the project up and running on your local machine for development and testing.

### Prerequisites

*   Python 3.12+
*   Node.js 18+ and npm (for frontend)
*   `uv` (recommended package manager for backend)
*   Docker and Docker Compose (for production-like local testing)

### 1. Clone the Repository

```bash
git clone https://github.com/kaziiriad/invoicing_application.git
cd invoicing_application/
```

### 2. Install Dependencies

Using `uv` (ensure `uv` is installed globally or via `pip install uv`):

```bash
uv sync
```

### 3. Environment Variables

Create a `.env` file in the `backend/` directory based on `backend/.env.template`:

```bash
cp backend/.env.template backend/.env
```

Edit `backend/.env` and fill in your `SECRET_KEY` and `DATABASE_URL`. For local development, you can use SQLite:

```
SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3 # For local setup only. Use posgreSQL for production environment
```

### 4. Database Setup

Apply migrations to create the database schema:

```bash
uv run -- python backend/manage.py makemigrations users invoicing
uv run -- python backend/manage.py migrate
```

### 5. Create a Superuser (for Admin Panel Access)

```bash
uv run -- python backend/manage.py createsuperuser
```

### 6. Seed Initial Data

Populate the database with some sample items and inventory:

```bash
uv run -- python backend/manage.py seed_inventory
```

### 7. Run the Backend Development Server

```bash
uv run -- python backend/manage.py runserver 0.0.0.0:8000
```

The API will be accessible at `http://127.0.0.1:8000/api/`.

## Frontend Setup

The frontend is a **fully implemented React TypeScript application** built with Vite and modern UI libraries including shadcn/ui, Tailwind CSS, and React Query.

#### Technology Stack
- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite
- **UI Components:** shadcn/ui with Radix UI
- **Styling:** Tailwind CSS
- **HTTP Client:** Axios with React Query
- **State Management:** React Context API
- **Form Handling:** React Hook Form with Zod validation
- **Routing:** React Router v6
- **Icons:** Lucide React

#### Features Implemented
✅ **Authentication:** Login/logout with JWT token management  
✅ **Dashboard:** Statistics overview and recent invoices  
✅ **Invoice Management:** Create, view, edit, pay, and cancel invoices  
✅ **Responsive Design:** Mobile-first with dark/light theme support  
✅ **Real-time Updates:** React Query for optimistic updates  
✅ **Type Safety:** Full TypeScript integration with API types

#### Setup Instructions

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    # or bun install (if you prefer bun)
    ```

3.  **Environment Variables:**
    The `.env` file is already configured with:
    ```
    VITE_API_URL=http://localhost:8000/api
    ```

4.  **Run the development server:**
    ```bash
    npm run dev
    ```
    The application will be available at `http://localhost:8080`. You can access the registration page at `http://localhost:8080/register`.

#### Available Scripts
```bash
npm run dev          # Start development server
npm run build        # Build for production  
npm run build:dev    # Build in development mode
npm run lint         # Run ESLint
npm run preview      # Preview production build
```

## Running the Full Application (Backend + Frontend)

To run both the backend and frontend simultaneously for local development:

1.  **Start the Backend Server** (in a separate terminal):
    ```bash
    cd backend
    uv run -- python manage.py runserver 0.0.0.0:8000
    ```

2.  **Start the Frontend Development Server** (in another separate terminal):
    ```bash
    cd frontend
    npm run dev
    ```

Once both servers are running:
- **Frontend Application:** `http://localhost:8080` (React app)
- **Backend API:** `http://localhost:8000/api/` (Django REST API)
- **API Documentation:** `http://localhost:8000/swagger/` (Swagger UI)


## API Endpoints

All API endpoints are prefixed with `/api/`.

### Authentication

*   **`POST /api/users/register/`**: Register a new user.
    *   **Request Body:** `{"username": "...", "email": "...", "password": "...", "password2": "..."}`
    *   **Response:** User data, `access` and `refresh` JWT tokens.
*   **`POST /api/token/`**: Obtain JWT access and refresh tokens.
    *   **Request Body:** `{"username": "...", "password": "..."}`
    *   **Response:** `access` and `refresh` JWT tokens.
*   **`POST /api/token/refresh/`**: Refresh an expired access token using a refresh token.
    *   **Request Body:** `{"refresh": "..."}`
    *   **Response:** New `access` token.
*   **`POST /api/users/logout/`**: Blacklist a refresh token to log out.
    *   **Request Body:** `{"refresh": "..."}`
    *   **Response:** `205 Reset Content` on success.

### Invoices (Requires Authentication)

*   **`GET /api/invoices/`**: List all invoices.
*   **`POST /api/invoices/`**: Create a new invoice.
    *   **Request Body:** `{"customer_name": "...", "due_date": "YYYY-MM-DD", "items": [{"item": <item_id>, "quantity": <int>}]}`
*   **`GET /api/invoices/{id}/`**: Retrieve details of a specific invoice.
*   **`PATCH /api/invoices/{id}/`**: Partially update a pending invoice (e.g., customer details, due date).
*   **`PUT /api/invoices/{id}/`**: Fully update a pending invoice (e.g., customer details, due date).
*   **`POST /api/invoices/{id}/pay/`**: Mark a pending invoice as paid.
    *   **Request Body (Optional):** `{"notes": "..."}`
*   **`POST /api/invoices/{id}/cancel/`**: Cancel a pending invoice and release allocated stock.

### API Documentation

Access the interactive API documentation at:
*   **Swagger UI:** `http://127.0.0.1:8000/swagger/`
*   **ReDoc:** `http://127.0.0.1:8000/redoc/`

## Docker Deployment

### Quick Start with Docker (Recommended)

Use the provided helper script for easy Docker management:

```bash
# Make script executable
chmod +x docker-dev.sh

# Start all services (backend + frontend + database)
./docker-dev.sh start

# View status
./docker-dev.sh status

# View logs
./docker-dev.sh logs

# Stop services
./docker-dev.sh stop
```

Your complete application will be available at:
- **🌐 Full Application:** `http://localhost:80` (React frontend)
- **🔧 Backend API:** `http://localhost:80/api/`
- **📚 API Documentation:** `http://localhost:80/swagger/`
- **🗄️ Database:** `localhost:5432`

### Docker Architecture

The containerized setup includes:

1. **Frontend Container**: React app built with Vite and served via nginx
2. **Backend Container**: Django REST API with Gunicorn
3. **Nginx Proxy**: Routes frontend and API requests, serves static files
4. **PostgreSQL Database**: Production-ready database

### Docker Helper Script Commands

```bash
./docker-dev.sh start          # Build and start all services
./docker-dev.sh stop           # Stop all services  
./docker-dev.sh restart        # Restart services
./docker-dev.sh logs [service] # View logs
./docker-dev.sh status         # Show service status
./docker-dev.sh cleanup        # Clean up Docker resources

# Run commands in containers
./docker-dev.sh backend 'python manage.py migrate'
./docker-dev.sh backend 'python manage.py createsuperuser'
./docker-dev.sh frontend 'npm run build'
```

### Manual Docker Compose

If you prefer to use docker-compose directly:

```bash
# Start services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build --force-recreate
```

### Production Deployment

For production deployment:

1. **Environment Variables**: Update `backend/.env` for production:
   ```
   SECRET_KEY=your_production_secret_key_here
   DEBUG=False
   ALLOWED_HOSTS=your_domain.com,www.your_domain.com
   DATABASE_URL=postgresql://user:password@postgres:5432/dbname
   ```

2. **SSL/HTTPS**: Add SSL certificates to nginx configuration

3. **Domain Setup**: Update nginx.conf with your domain

4. **Database**: Use managed PostgreSQL service or secure the container

5. **Deploy**: 
   ```bash
   ./docker-dev.sh start
   ```

### Container Services

| Service | Container | Port | Purpose |
|---------|-----------|------|---------|
| Frontend | `react_frontend` | - | React app build artifacts |
| Backend | `django_backend` | 8000 | Django REST API |
| Nginx | `nginx_proxy` | 80 | Reverse proxy & static files |
| Database | `postgres_db` | 5432 | PostgreSQL database |

### Volumes

- `frontend_volume`: Stores built React app files
- `static_volume`: Django static files (admin, DRF UI)
- `postgres_volume`: Database persistence

---

This `README.md` provides a comprehensive overview, setup instructions, API details, and justifications for key design decisions.
