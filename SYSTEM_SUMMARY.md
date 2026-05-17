# FinTrack - Personal Finance Tracker

FinTrack is a comprehensive personal finance tracking application designed with a gamification and rewards system to encourage healthy financial habits. It allows users to track income and expenses, set budget limits, and earn rewards through streaks and challenges.

## Tech Stack

- **Backend:** Django (latest stable)
- **Frontend:** Django Templates + HTMX + Tailwind CSS (via CDN)
- **Charts:** Chart.js (loaded via CDN)
- **Database:** SQLite (development), PostgreSQL (production)
- **Authentication:** Django built-in `django.contrib.auth`

## Core Features

### Accounts
- **F-01: Authentication:** Secure sign-up and login functionality.
- **F-02: User Profile:** Displays avatars, bios, current points, badges, streaks, and monthly summaries.

### Recording Money
- **F-03: Add Record:** Quick entry for income/expense with HTMX updates.
- **F-04: Manage Records:** Edit or delete existing records.
- **F-05: Record List:** Filterable and sortable view of all transactions.
- **F-06: Categories:** Predefined categories (Food, Rent, Transport, etc.) classified as Need, Want, or Saving.

### Dashboard & Budget Tools
- **F-07: Overview:** Monthly income, expense, and balance summary with Chart.js visualizations.
- **F-08: Category Limits:** User-defined spending limits with progress tracking.
- **F-09: 50/30/20 Breakdown:** Doughnut chart showing spending by classification vs. benchmarks.
- **F-10: Savings Runway:** Calculation of remaining days based on daily spend.
- **F-11: Unusual Spending Alert:** Automated flagging of high spending relative to historical averages.

### Rewards & Gamification
- **F-12: Points:** Earned for daily logging activity.
- **F-13: Streaks:** Tracks consecutive days of financial tracking.
- **F-14: Badges:** Awarded for milestones (e.g., first record, 7-day streak).
- **F-15: Weekly Challenges:** Active goals to encourage budget adherence.

### Alerts & Notifications
- **F-16: Budget Warning:** Alerts when reaching 80% of a category limit.
- **F-17: Weekly Recap:** Monday summaries of previous week's performance.

## Architectural Philosophy

- **Simplicity First:** Straightforward, readable code over clever abstractions.
- **HTMX Driven:** Partial page updates for a modern feel without the complexity of SPA frameworks.
- **Service Layer Pattern:** Business logic resides in `services.py` or `utils.py`.
- **Consistent Structure:** Clear separation between models, views, and templates.

## Project Structure

- `apps/`: Contains functional modules of the application.
  - `account/`: User management, profiles, and auth logic.
  - `AI/`: AI-powered financial advice and chatbot services.
  - `dashboard/`: Core dashboard views and financial calculations.
  - `tracker/`: Transaction logging, category management, and budgeting.
- `core/`: Project configuration, settings, and root URLs.
- `templates/`: Global templates and shared layouts.
- `manage.py`: Django project management script.
- `requirements.txt`: Python dependencies.
- `GEMINI.md`: Project-specific developer instructions.
