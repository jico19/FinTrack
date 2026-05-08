# FinTrack Development Plan & Progress

This document tracks the development of FinTrack, a personal money tracker with a rewards system.

## 🚀 Completed Tasks

### 1. Accounts
- [x] **F-01 Sign up & log in** - Basic registration and login views are implemented.
  - `RegisterView` in `apps/account/views.py`
  - `LoginView` (Django built-in) used in `apps/account/urls.py`
  - Templates: `login.html`, `register.html`
- [x] **User Profile Model** - `UserProfile` model created to store bio, profile pic, and points.

### 2. Recording Money
- [x] **Budget Record Model** - `BudgetRecord` model created with support for income/expense, categories (Needs/Wants/Savings), and notes.
- [x] **F-03 Add a record** - Basic `CreateBudgetRecord` view and form implemented.
  - `CreateBudgetRecord` in `apps/tracker/views.py`
  - `BudgetRecordForms` in `apps/tracker/forms.py`
  - Template: `create_budget_record.html`

### 3. Dashboard
- [x] **F-07 Money overview** - Basic dashboard view created.
  - `HomePageView` in `apps/dashboard/views.py`
  - Template: `dashboard.html` (currently lists all records)
- [x] **✨ Surprise AI Feature** - Smart financial insights using Gemini AI (with heuristic fallback).
- [x] **F-08 Set a monthly limit** - `spending_limit` field exists in `BudgetRecord` model.

---

## 📅 Pending Tasks (TODO)

### 1. Accounts
- [ ] **F-02 Profile page** - Create a view and template to display user details, points, badges, and streaks.
- [ ] **Profile Update** - Add ability for users to update their bio and profile picture.

### 2. Recording Money
- [ ] **F-04 Edit or remove a record** - Implement UpdateView and DeleteView for `BudgetRecord`.
- [ ] **F-05 View all records (Filtering)** - Enhance the records view with filters for category, type, and date.
- [ ] **F-06 Spending categories (Refinement)** - Ensure categories are strictly categorized into Needs, Wants, and Savings in the UI.

### 3. Dashboard
- [ ] **F-07 Money overview (Visuals)** - Add summary cards for total income, total expense, and balance. Add spending charts.
- [ ] **F-08 Spending Limit Logic** - Add progress bars to show how close the user is to their limits.

### 4. Budget Tools
- [ ] **F-09 Needs / Wants / Savings breakdown** - Implement logic to calculate and display the percentage breakdown.
- [ ] **F-10 How long will money last** - Logic to estimate "burn rate" and remaining days.
- [ ] **F-11 Unusual spending warning** - Logic to compare current spending with the 3-month average.

### 5. Rewards (The "Fun" Part)
- [ ] **F-12/F-13 Streaks** - Implement logic to track daily logging and update streaks.
- [ ] **F-14 Badges** - Create a Badge model and logic to award them (e.g., "First Record", "7-Day Streak").
- [ ] **F-15 Weekly challenges** - Implement weekly goals and bonus point system.

### 6. Alerts
- [ ] **F-16 Budget warning** - Logic to trigger warnings at 80% limit.
- [ ] **F-17 Weekly recap** - Monday summary logic and dashboard notification.

---

## 🛠️ Infrastructure & UI
- [ ] **Base Template Refinement** - Improve `base.html` and `navbar.html` for better navigation.
- [ ] **Styling** - Apply a consistent CSS theme (e.g., using Vanilla CSS or a framework as per project preference).
- [ ] **Signals** - Use Django signals to automatically create `UserProfile` when a `User` is registered.
