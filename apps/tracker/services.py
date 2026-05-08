from datetime import date, timedelta
from django.utils import timezone
from django.db.models import Sum
from apps.account.models import UserProfile, Badge, UserBadge, Challenge, UserChallengeProgress
from apps.tracker.models import BudgetRecord

def get_monthly_summary(user, year, month):
    """
    Calculate total income, expense, and net balance for a given month/year.
    """
    records = BudgetRecord.objects.filter(user=user, date__year=year, date__month=month)
    income = records.filter(spending_type=BudgetRecord.Type.INCOME).aggregate(Sum('amount'))['amount__sum'] or 0
    expense = records.filter(spending_type=BudgetRecord.Type.EXPENSE).aggregate(Sum('amount'))['amount__sum'] or 0
    balance = income - expense
    return income, expense, balance

def update_user_gamification(user):
    """
    F-12: Earn points for each day the user logs at least one record.
    F-13: Current streak increases by 1 each day a record is logged. 
    F-14: Check and award badges.
    F-15: Update challenge progress.
    """
    profile, created = UserProfile.objects.get_or_create(user=user)
    today = date.today()
    
    if profile.last_logged_date != today:
        profile.total_points += 10 # Award points for logging today
        if profile.last_logged_date == today - timedelta(days=1):
            profile.current_streak += 1
        else:
            profile.current_streak = 1
        
        if profile.current_streak > profile.best_streak:
            profile.best_streak = profile.current_streak
        
        profile.last_logged_date = today
        profile.save()
    
    # Check milestones
    check_and_award_badges(profile)
    
    # Update active challenges
    update_challenges_progress(user)
    
    return profile

def check_and_award_badges(profile):
    user = profile.user
    if BudgetRecord.objects.filter(user=user).exists():
        award_badge(user, "First Step", "Logged your first financial record!")
    if profile.current_streak >= 7:
        award_badge(user, "Week Warrior", "Logged transactions for 7 days in a row!")
    if profile.total_points >= 100:
        award_badge(user, "Centurion", "Reached 100 total points!")
    if BudgetRecord.objects.filter(user=user, category__classification="SAVING").exists():
        award_badge(user, "Future Planner", "Logged your first saving or investment!")
    
    # F-14: Under budget for a full month
    check_monthly_budget_badge(user)

def check_monthly_budget_badge(user):
    """
    Awards 'Budget Master' if the user stayed under all category limits in the previous month.
    """
    today = date.today()
    # Go back to the first day of the current month, then subtract 1 day to get the previous month
    first_day_this_month = today.replace(day=1)
    last_day_prev_month = first_day_this_month - timedelta(days=1)
    prev_month_start = last_day_prev_month.replace(day=1)
    
    # Get all limits for that month
    from apps.tracker.models import CategoryLimit
    limits = CategoryLimit.objects.filter(user=user, month=prev_month_start)
    
    if not limits.exists():
        return

    all_under = True
    for limit in limits:
        spent = BudgetRecord.objects.filter(
            user=user, 
            category=limit.category,
            spending_type=BudgetRecord.Type.EXPENSE,
            date__range=[prev_month_start, last_day_prev_month]
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        if spent > limit.limit_amount:
            all_under = False
            break
    
    if all_under:
        award_badge(user, "Budget Master", f"Stayed under all category limits for {prev_month_start.strftime('%B %Y')}!")

def award_badge(user, name, description):
    badge, _ = Badge.objects.get_or_create(name=name, defaults={'description': description})
    UserBadge.objects.get_or_create(user=user, badge=badge)

def update_challenges_progress(user):
    """
    F-15: Progress active challenges when a record is logged.
    """
    active_challenges = Challenge.objects.filter(is_active=True)
    for challenge in active_challenges:
        progress, created = UserChallengeProgress.objects.get_or_create(
            user=user,
            challenge=challenge
        )
        if not progress.is_completed:
            progress.current_count += 1
            if progress.current_count >= challenge.target_count:
                progress.is_completed = True
                progress.completed_at = timezone.now()
                # Reward bonus points
                profile = user.userprofile
                profile.total_points += challenge.points_reward
                profile.save()
                
                # F-15: Award badge on completion
                award_badge(user, "Challenge Crusher", f"Completed the weekly challenge: {challenge.title}!")
            progress.save()
