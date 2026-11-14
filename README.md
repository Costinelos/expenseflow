# ExpenseFlow API

Enterprise Expense Management & Approval Workflow REST API built with **Django** and **Django REST Framework**.

## Key Features
- **JWT Authentication & Role-Based Access Control (RBAC):** `ADMIN`, `MANAGER`, and `EMPLOYEE` roles with token blacklisting on logout.
- **Approval Workflow:** Status-driven lifecycle (`DRAFT` -> `SUBMITTED` -> `APPROVED` / `REJECTED`) with edit/delete locks on finalized expenses and manager `approval_limit` enforcement.
- **Receipt Handling:** File upload validation for images (`.jpg`, `.png`) and `.pdf` documents (max 5 MB).
- **Reporting & Exports:** Real-time SQL aggregations (`/api/expenses/summary/`) and CSV export (`/api/expenses/export-csv/`).
- **Interactive API Docs:** OpenAPI 3.0 schema & Swagger UI at `/api/docs/`.

## Quick Start

```bash
# 1. Activate virtual environment & install dependencies
pip install -r requirements.txt

# 2. Run migrations & start development server
python manage.py migrate
python manage.py runserver

# 3. Run automated test suite
python manage.py test apps.expenses -v 2
