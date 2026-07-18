# FitSteps Backend - Comprehensive Working Explanation

## 1. Overview and Architecture
The FitSteps backend is a robust RESTful API built with **FastAPI**. It handles all data persistence, authentication, business logic, and third-party AI integrations.

**Key Architectural Decisions:**
- **Framework:** FastAPI was chosen for its high performance, automatic OpenAPI (Swagger) documentation, and native async support.
- **Database:** PostgreSQL (hosted on Neon) provides reliable, relational data storage. SQLAlchemy is used as the ORM (Object Relational Mapper) to interact with the database using Python objects rather than raw SQL strings.
- **Migrations:** Alembic tracks and applies changes to the database schema over time.
- **Dependency Injection:** FastAPI's `Depends` system is heavily utilized to inject database sessions and authenticate users on a per-route basis safely.

---

## 2. Authentication Logic (`api/auth.py`)
FitSteps uses JWT (JSON Web Tokens) for secure, stateless authentication.

### A. User Registration (`/auth/register`)
1. **Validation:** When a new user submits their details, the Pydantic schema (`UserCreate`) strictly validates that the email is a valid string and passwords meet criteria.
2. **Hashing:** Passwords are **never** stored in plain text. The backend uses the `passlib` library with the `bcrypt` algorithm to irreversibly hash the password before saving it to the PostgreSQL database.
```python
hashed_password = get_password_hash(user.password)
db_user = models.User(email=user.email, hashed_password=hashed_password, name=user.name)
```

### B. Login and Token Generation (`/auth/login`)
1. **Verification:** The user submits their email and plain-text password. The backend queries the database for the email, and uses `bcrypt.verify()` to check if the plain-text password matches the stored hash.
2. **JWT Creation:** If verified, the server generates a JWT containing the user's `user_id` inside the payload (`sub` claim). The token is signed using a secret key (`settings.SECRET_KEY`) and an algorithm (`HS256`).
3. **Response:** The token is returned to the frontend, which will send it back in the `Authorization: Bearer <token>` header on subsequent requests.

### C. Protecting Routes (`api/dependencies.py`)
To secure endpoints (like `/activities/`), we use a dependency function `get_current_user`.
```python
@router.get("/")
def get_activities(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
```
Whenever a route includes `Depends(get_current_user)`, FastAPI automatically intercepts the request, reads the `Bearer` token, verifies the cryptographic signature, extracts the `user_id`, and fetches the user from the database. If any of these steps fail, it instantly throws a `401 Unauthorized` exception before the route's code even runs.

---

## 3. Database & ORM Logic
SQLAlchemy bridges the gap between Python and PostgreSQL.

### Models (`db/models.py`) vs Schemas (`schemas/*.py`)
- **Models:** Define the actual structure of the PostgreSQL tables. They dictate column types (Integer, String) and relationships (Foreign Keys).
- **Schemas (Pydantic):** Define exactly what data the API expects to receive (e.g., `ActivityCreate`) and what it promises to return (e.g., `ActivityResponse`). They handle JSON validation and serialization.

### Example: Calculating Analytics (`api/analytics.py`)
The backend calculates complex statistics directly in the database engine (PostgreSQL) rather than pulling all rows into Python memory. This is exponentially faster.

**Best Day Calculation:**
```python
best_day = db.query(
    func.date(models.Activity.activity_date).label('date'),
    func.sum(models.Activity.steps).label('total_steps')
).filter(
    models.Activity.user_id == current_user.id
).group_by(
    text('1') # PostgreSQL specific syntax to group by the 1st selected column
).order_by(
    func.sum(models.Activity.steps).desc()
).first()
```
**Logic Breakdown:**
1. Group all activities by their calendar date (`func.date`).
2. Add up the steps for each date (`func.sum`).
3. Ensure we only look at the logged-in user's data (`filter`).
4. Sort the result so the highest step count is at the very top (`desc()`).
5. Grab the top row (`first()`).

---

## 4. Gamification Logic (`api/gamification.py` & `api/activities.py`)
The backend is the sole authority on whether a user earns a badge.

### Badge Evaluation Logic
Whenever a user makes a `POST /activities/` request, the `create_activity` function executes and then immediately calls a helper function `award_badge()` to evaluate milestones.

**Example Implementation:**
```python
# Check for 10k Club badge
if activity.steps >= 10000:
    award_badge("10k Club")
```
The `award_badge("10k Club")` function:
1. Queries the `badges` table to find the ID of the "10k Club" badge.
2. Queries the `user_badges` bridge table to see if this `user_id` already has this `badge_id`.
3. If they don't have it, it creates a new `UserBadge` record, permanently awarding it to them.

### Streak Calculation Logic
When logging an activity, the backend checks the user's `last_active_date`.
- If the user was last active **yesterday**, their `current_streak` is incremented by +1.
- If the user was last active **today**, the streak stays the same (they already got credit for today).
- If the user was last active **before yesterday**, their streak is broken and reset to `1`.
- The `longest_streak` is simply updated if `current_streak` grows larger than it.

---

## 5. Gemini AI Integration (`api/ai.py`)
The backend provides a smart, personalized step goal using Google's Gemini LLM.

### AI Processing Logic
1. **Data Gathering:** The backend queries the database for all activities the user logged over the last exactly 7 days.
2. **Context Building:** It formats this raw database data into a clean JSON summary.
3. **Prompt Engineering:** It injects the JSON summary into a highly specific prompt instructing the Gemini model to act as a fitness coach and output its response strictly in JSON format.
4. **Execution:** It sends the prompt to the `gemini-flash-latest` model.
5. **Fallback Safety:** If the Gemini API key is missing or the external API goes down (500 error), a generic try/catch block catches the failure and instantly returns a hardcoded "Fallback" recommendation so the frontend doesn't crash.
