<div align="center">
  <img src="https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/database.svg" alt="Backend Icon" width="80" height="80">
  <h1 align="center">FitSteps Backend</h1>
  <p align="center">
    <strong>A high-performance RESTful API powering the FitSteps ecosystem.</strong>
  </p>
</div>

<hr />

## ✨ Features

- ⚡ **FastAPI Powered:** Extremely fast execution and asynchronous routing out of the box.
- 🔒 **Secure Authentication:** JSON Web Token (JWT) based authentication with Bcrypt password hashing.
- 🗄️ **Robust Database:** SQLAlchemy ORM integrated with a PostgreSQL database (hosted via Neon). 
- 🤖 **AI Integration:** Seamless integration with Google's `gemini-flash-latest` AI model to provide personalized fitness coaching and daily step goals.
- 🏅 **Server-Side Gamification:** Badges and streaks are securely calculated on the server to prevent cheating.
- 📖 **Auto-Generated Docs:** Provides interactive Swagger UI documentation at `/docs` out of the box.

## 🛠️ Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Language:** Python 3.9+
- **Database:** [PostgreSQL](https://www.postgresql.org/)
- **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/)
- **Migrations:** [Alembic](https://alembic.sqlalchemy.org/)
- **AI Integration:** [Google Generative AI (Gemini)](https://ai.google.dev/)

## 🚀 Quick Start (Local Setup)

### Prerequisites
- Python 3.9 or higher
- A PostgreSQL database (Local or Cloud like Neon/Supabase)

### 1. Clone & Install
```bash
git clone https://github.com/jibin7jose/fitsteps-backend.git
cd fitsteps-backend

# Create a virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate
# Activate it (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the root of the `fitsteps-backend` folder and add the following:
```env
# Essential
DATABASE_URL=postgresql://username:password@localhost:5432/fitsteps
SECRET_KEY=your_super_secret_jwt_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Optional (Required for AI coaching features)
GEMINI_API_KEY=your_google_gemini_api_key_here
```

### 3. Database Setup (Migrations)
Before running the app, apply the database migrations to create the tables.
```bash
alembic upgrade head
```

*(Optional)* Seed the gamification badges into your database:
```bash
# You can do this by hitting the endpoint once the server is running:
curl -X POST http://localhost:8000/gamification/seed-badges
```

### 4. Run the Server
```bash
uvicorn main:app --reload
```
The API will start at `http://localhost:8000`. 
Visit `http://localhost:8000/docs` to see the interactive Swagger API documentation!

## 📁 Project Structure

* **`/api`** - Contains all the router endpoints (auth, activities, ai, analytics, gamification)
* **`/core`** - Configuration and environment variable management
* **`/db`** - Database connection, SQLAlchemy models, and session management
* **`/schemas`** - Pydantic models for strict Request/Response data validation
* **`/alembic`** - Database migration scripts
* **`/docs`** - Comprehensive technical documentation and internal logic explanation

---
*Built with ❤️ for fitness enthusiasts.*
