# AI Development Rules and Guidelines

This document outlines the core technologies and best practices for developing the Zidisha Loyalty Platform, with a focus on AI-related components.

## Tech Stack Overview

The Zidisha Loyalty Platform is built using a modern, robust, and scalable tech stack:

*   **Frontend:** A React application powered by Next.js and TypeScript, styled with Tailwind CSS and utilizing shadcn/ui components.
*   **Backend:** A Python-based API built with FastAPI, designed for high performance and asynchronous operations.
*   **Database:** PostgreSQL, an advanced open-source relational database, managed asynchronously with SQLAlchemy.
*   **Caching & Task Queue:** Redis is used for high-speed data caching and as a broker for Celery background tasks.
*   **Background Tasks:** Celery handles asynchronous and scheduled tasks, crucial for long-running AI model training and bulk notifications.
*   **AI/ML:** Python libraries like Pandas, NumPy, and Scikit-learn are used for data processing, model training, and predictive analytics.
*   **External APIs:** Integration with external services like M-Pesa Daraja API and Africa's Talking for transactions and SMS notifications.
*   **Containerization:** Docker and Docker Compose are used to manage and orchestrate all services for consistent development and deployment.

## Library Usage Rules

To maintain consistency, performance, and ease of maintenance, please adhere to the following library usage rules:

### Frontend Development

*   **Framework:** Always use **React** within the **Next.js** framework.
*   **Language:** All frontend code must be written in **TypeScript**.
*   **Styling:** Use **Tailwind CSS** exclusively for all styling. Avoid inline styles or custom CSS files unless absolutely necessary for third-party components that cannot be styled otherwise.
*   **UI Components:** Utilize **shadcn/ui** components, which are built on **Radix UI**. Do not modify the source files of shadcn/ui components directly. If a custom variation is needed, create a new component that wraps or extends the shadcn/ui component.
*   **Icons:** Use icons from the **`lucide-react`** library.
*   **HTTP Requests:** Use **`axios`** for all API calls to the backend.
*   **Data Fetching:** Implement data fetching and caching in React components using **`swr`**.
*   **Charting:** For all data visualization and charts, use **`recharts`**.
*   **Date Manipulation:** Use **`date-fns`** for formatting, parsing, and manipulating dates.
*   **Animations:** For advanced UI animations, use **`gsap`**.
*   **Supabase:** If integrating with Supabase for specific features, use the **`@supabase/supabase-js`** client.

### Backend Development

*   **API Framework:** All API endpoints must be built using **FastAPI**.
*   **Database ORM:** Use **SQLAlchemy** with **`asyncpg`** for all asynchronous database interactions with PostgreSQL.
*   **Data Validation/Serialization:** Use **Pydantic** for defining all request and response schemas.
*   **Password Hashing:** Use **`passlib`** for secure password hashing and verification.
*   **JWT Handling:** Use **`python-jose`** for creating and verifying JSON Web Tokens (JWTs).
*   **HTTP Requests (Outgoing):** Use **`httpx`** for making all outgoing asynchronous HTTP requests to external services (e.g., Daraja API, Africa's Talking).
*   **AI/ML Libraries:**
    *   **Data Manipulation:** Use **`pandas`** and **`numpy`** for data loading, preprocessing, and numerical operations within AI services.
    *   **Machine Learning:** Use **`scikit-learn`** for building and training machine learning models (e.g., `RandomForestClassifier`, `RandomForestRegressor`).
    *   **Model Persistence:** Use **`joblib`** for saving and loading trained machine learning models.
*   **Background Tasks:** Use **Celery** for defining and managing all background and scheduled tasks. **Redis** should be configured as the broker and backend for Celery.
*   **Logging:** Use Python's standard **`logging`** module for all application logging.