AI Email Reply Drafting API

An AI-powered email reply drafting application that transforms an incoming email and a user's rough response instruction into a clear, purposeful, structured email reply.
The project is built as a reliable AI backend service rather than a simple LLM wrapper. It includes JWT authentication, user-owned sessions, PostgreSQL persistence, structured AI output, scope guardrails, controlled error handling, and transaction rollback.

Features
- User signup and JWT-based login
- Protected API endpoints
- User-owned email drafting sessions
- PostgreSQL persistence with SQLAlchemy ORM
- Structured AI-generated replies:
  - Subject
  - Greeting
  - Body
  - Closing
- User-selected tone
- Scope guardrail for out-of-scope requests
- Controlled AI/API error responses
- Database rollback on failed operations
- Conversation history
- Simple HTML/CSS/JavaScript frontend
- Groq LLM integration
- FastAPI Swagger/OpenAPI documentation
- CORS configuration for frontend/backend communication

Problem
People often know what they want to say in response to an email but struggle to turn their rough idea into a professional and purposeful reply.
This application allows the user to provide:
1. The incoming email
2. A rough instruction describing what they want to say
3. The desired tone
The system then generates a structured email reply while preserving the user's intended meaning.

Example
Input
Incoming email
I hope this email finds you well. I am writing to request an update on the project timeline for the upcoming marketing campaign. Could you please let me know if we are still on track for the Friday deadline?

Instruction
Tell them I'm available at 10 AM to discuss the timeline.

Tone
Professional

Output
The AI generates a structured response containing a subject, greeting, body, and closing.
Architecture
                    ┌──────────────────────┐
                    │      Frontend        │
                    │   HTML / CSS / JS    │
                    └──────────┬───────────┘
                               │ HTTP
                               ▼
                    ┌──────────────────────┐
                    │       FastAPI        │
                    │     API Layer        │
                    └──────────┬───────────┘
                               │
                  ┌────────────┴────────────┐
                  │                         │
                  ▼                         ▼
        ┌──────────────────┐      ┌──────────────────┐
        │   JWT Auth &     │      │  Scope Guardrail │
        │  Authorization   │      │                  │
        └────────┬─────────┘      └────────┬─────────┘
                 │                         │
                 └────────────┬────────────┘
                              ▼
                    ┌──────────────────────┐
                    │    Groq AI Service   │
                    │ Structured JSON      │
                    │ Email Generation     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ PostgreSQL Database  │
                    │                      │
                    │ users                │
                    │ sessions             │
                    │ messages             │
                    └──────────────────────┘
Request Flow
Client Request
     ↓
JWT Authentication
     ↓
Session Ownership Check
     ↓
Pydantic Input Validation
     ↓
Scope Guardrail
     ↓
Groq AI Generation
     ↓
Structured Output Validation
     ↓
Create User + Assistant Messages
     ↓
Single Database Commit
     ↓
Return Structured Response
For failed operations:
Failure
   ↓
Rollback
   ↓
Controlled HTTP Error
   ↓
No partially committed successful interaction
API Endpoints
Method	Endpoint	Purpose
POST	/signup	Create a user
POST	/login	Authenticate and receive JWT
POST	/logout	Planned session/logout endpoint
POST	/sessions	Create an email drafting session
GET	/sessions	Get the authenticated user's sessions
POST	/sessions/{session_id}/messages	Generate an AI email reply
GET	/sessions/{session_id}/messages	Retrieve conversation history


Authentication and Authorization
JWT authentication is used to identify authenticated users.
Authentication alone is not sufficient for accessing a session. Every session-based operation verifies that the requested session belongs to the authenticated user.
This prevents one user from accessing another user's conversations.
Passwords are hashed using bcrypt before storage.
Database Design
The application uses three main tables:
users
- id
- email
- hashed_password
- created_at
sessions
- id
- user_id
- created_at
- updated_at
messages
- id
- session_id
- role
- content
- created_at
content is stored as PostgreSQL JSONB so user requests and structured assistant responses can be persisted without losing their structure.
Relationship:
User
 └── Sessions
      └── Messages
AI Behavior
The user controls the requested tone. The AI does not select a different tone.
The generation layer follows these principles:
- Draft only email replies
- Preserve the user's intended meaning
- Do not invent unsupported facts
- Use information from the incoming email and user instruction
- Return predictable structured output
Scope Guardrail
Before email generation, the request passes through a dedicated scope check.
For example:
Incoming email: What is FastAPI?
Instruction: Tell answer of it
This is not an email-reply drafting request.
The guardrail rejects it with a controlled 400 Bad Request response instead of generating an unrelated email.
Error Handling
The application distinguishes between different failure types:
Situation	Response
Invalid/out-of-scope request	400 Bad Request
Invalid authentication	401 Unauthorized
Missing session	404 Not Found
AI rate limit/quota	429 Too Many Requests
Invalid AI output	502 Bad Gateway
AI service unavailable	503 Service Unavailable
Unexpected application/database error	500 Internal Server Error


Database rollback is performed when a request fails after entering the database workflow.
Transaction Safety
The application avoids committing the user message and assistant message separately.
The successful flow is:
Generate AI result
       ↓
Validate AI result
       ↓
Create user message
       ↓
Create assistant message
       ↓
Commit once
If the operation fails:
Rollback
This prevents a failed AI request from being committed as a completed interaction.
Tech Stack
Backend
- Python
- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn
Authentication & Security
- JWT
- python-jose
- bcrypt / Passlib
- Session ownership authorization
- CORS
Database
- PostgreSQL
- SQLAlchemy ORM
- PostgreSQL JSONB
AI
- Groq API
- openai/gpt-oss-20b
- Structured JSON output
Frontend
- HTML
- CSS
- JavaScript
Development
- Git
- GitHub
- VS Code
- FastAPI Swagger/OpenAPI
Project Structure
AI-email-reply/
│
├── main.py
├── database.py
├── auth.py
├── requirements.txt
├── .env.example
├── .gitignore
│
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── session.py
│   └── message.py
│
├── schemas/
│   ├── user.py
│   ├── session.py
│   └── message.py
│
├── routes/
│   ├── auth.py
│   ├── sessions.py
│   └── messages.py
│
├── services/
│   └── groq.py
│
└── frontend/
    ├── index.html
    ├── login.html
    ├── signup.html
    ├── style.css
    └── script.js
Adjust the structure above if your final local filenames differ.
Environment Variables
Create a .env file locally:
DATABASE_URL=your_postgresql_connection_string
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
GROQ_API_KEY=your_groq_api_key
Never commit .env or API keys to GitHub.
An example environment file is included as .env.example.
Local Setup
1. Clone the repository
git clone [https://github.com/akdss-AI/AI-Email-Reply-Assistant.git]
cd ai-email-reply-drafting-api
2. Create a virtual environment
Windows:
python -m venv venv
venv\Scripts\activate
3. Install dependencies
pip install -r requirements.txt
4. Configure environment variables
Create .env using the variables described above.
5. Start the backend
uvicorn main:app --reload
Backend:
http://127.0.0.1:8000
Swagger documentation:
http://127.0.0.1:8000/docs
6. Start the frontend
From the project root:
cd frontend
python -m http.server 8080
Open:
http://127.0.0.1:8080
Testing
The application was tested through the following workflow:
1. User signup
2. User login
3. JWT authorization
4. Session creation
5. Valid email drafting request
6. Structured AI response
7. Conversation history retrieval
8. Out-of-scope request
9. Controlled guardrail error
10. Database rollback verification
11. Re-check conversation history after failure
Deployment
The recommended deployment architecture is:
Render Static Site
       │
       │ HTTPS
       ▼
Render FastAPI Web Service
       │
       ├── Groq API
       │
       └── PostgreSQL
The frontend and backend can be deployed separately while remaining part of the same GitHub repository.
After deployment, update the frontend API base URL from the local FastAPI address to the live backend URL.
Current Scope
Version 1 intentionally does not include:
- Automatic email sending
- Gmail integration
- Outlook integration
- Background email delivery
- Automatic tone selection
The application focuses on reliable email reply generation and backend engineering fundamentals.
Future Improvements
- Gmail / Outlook integration
- Email sending with explicit user approval
- Refresh-token authentication
- Rate limiting per user
- API usage analytics
- Automated tests
- Database migrations with Alembic
- Production logging and monitoring
- More advanced prompt/version management
- Deployment with CI/CD
Author
Aqdas Abbas
BS Software Engineering — Virtual University of Pakistan
GitHub: https://github.com/akdss-AI
LinkedIn: https://www.linkedin.com/in/aqdas-abbas-073936373/
Built as an independent AI backend project focused on reliable AI integration, backend architecture, structured outputs, authentication, guardrails, and database consistency.
