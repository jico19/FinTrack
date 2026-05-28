# FinTrack Templates

Overview of Django templates used in the FinTrack project. All HTMX logic (`hx-*` attributes) has been omitted for clarity.

## Core Templates

- **base.html**: The master layout. Includes CDNs for Tailwind CSS, DaisyUI, HTMX, and Chart.js. Defines the main `content` block and includes the `navbar.html`.
- **navbar.html**: The global navigation component. Contains links to Dashboard, Records, Profile, and Logout.

## Account App (`apps/account/templates/account/`)

- **login.html**: User login form.
- **register.html**: New user registration form.
- **profile.html**: User profile dashboard. Displays:
    - User stats (points, current streak, best streak).
    - Monthly money summary.
    - Collected badges gallery.
- **edit_profile.html**: Form to update user profile information (bio, avatar).

## Tracker App (`apps/tracker/templates/tracker/`)

- **dashboard.html**: The primary application view. Features:
    - **F-07/F-09**: Financial overview cards and Chart.js charts (Spending by Category, Needs/Wants/Savings).
    - **F-08**: Category spending limits with progress bars.
    - **F-11**: Unusual spending alerts.
    - **F-17**: Weekly recap banner.
- **record_list.html**: A dedicated page for viewing and filtering all financial records.
- **manage_budgets.html**: Page for managing category limits and settings.

### Tracker Partials (`apps/tracker/templates/tracker/partials/`)

- **add_record_form.html**: Modal/Inline form for adding a new income or expense record.
- **edit_record_form.html**: Form for editing an existing record.
- **record_list_table.html**: The table structure for the record list.
- **record_row.html**: A single table row representing one record.
- **category_limits.html**: The section of the dashboard showing progress bars for category budgets.
- **limit_edit_form.html**: Inline form to update a specific category's spending limit.
- **dashboard_content.html**: The main inner content of the dashboard, used for dynamic updates.

## AI App (`apps/AI/templates/AI/`)

- **chatbot_partial.html**: The floating chatbot interface container.
- **chat_messages_partial.html**: The list of messages within the chat history.
- **advice_partial.html**: A specific fragment for displaying AI-generated financial advice.
