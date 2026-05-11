import json
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from .models import Category, BudgetRecord, CategoryLimit
from .services import update_user_gamification, get_monthly_summary
from apps.account.models import UserProfile
from datetime import date, timedelta
from django.utils import timezone
import calendar

@login_required
def dashboard(request):
    """
    F-07: Money overview with Chart.js visualizations.
    """
    today = date.today()
    month_start = today.replace(day=1)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    # F-13: Real-time streak reset check
    display_streak = profile.current_streak
    if profile.last_logged_date and profile.last_logged_date < today - timedelta(days=1):
        display_streak = 0
    
    income, expense, balance = get_monthly_summary(request.user, today.year, today.month)
    
    # NEW LOGIC: Income increases your available budget for the month
    total_available_budget = profile.budget + income
    budget_remaining = total_available_budget - expense
    budget_percent = min((expense / total_available_budget * 100), 100) if total_available_budget > 0 else 0
    
    categories = Category.objects.all()
    month_records = BudgetRecord.objects.filter(user=request.user, date__year=today.year, date__month=today.month).select_related('category')
    
    cat_data, cat_labels = [], []
    for cat in categories:
        amt = month_records.filter(category=cat, spending_type=BudgetRecord.Type.EXPENSE).aggregate(Sum('amount'))['amount__sum'] or 0
        if amt > 0:
            cat_labels.append(cat.name); cat_data.append(float(amt))

    nws_labels = ["Needs", "Wants", "Savings"]
    nws_data = [
        float(month_records.filter(category__classification=Category.Classification.NEED, spending_type=BudgetRecord.Type.EXPENSE).aggregate(Sum('amount'))['amount__sum'] or 0),
        float(month_records.filter(category__classification=Category.Classification.WANT, spending_type=BudgetRecord.Type.EXPENSE).aggregate(Sum('amount'))['amount__sum'] or 0),
        float(month_records.filter(category__classification=Category.Classification.SAVING).aggregate(Sum('amount'))['amount__sum'] or 0),
    ]
    
    total_nws = sum(nws_data)
    nws_percents = [round((val / total_nws) * 100, 1) for val in nws_data] if total_nws > 0 else [0, 0, 0]

    daily_labels, daily_data = [], []
    for day in range(1, today.day + 1):
        daily_labels.append(f"{calendar.month_abbr[today.month]} {day}")
        daily_data.append(float(month_records.filter(date__day=day, spending_type=BudgetRecord.Type.EXPENSE).aggregate(Sum('amount'))['amount__sum'] or 0))

    days_passed = today.day
    daily_burn_rate = expense / days_passed if days_passed > 0 else 0
    runway_days = balance / daily_burn_rate if daily_burn_rate > 0 and balance > 0 else 0
    runway_is_low = int(runway_days) < 30 and int(runway_days) > 0
    
    three_months_ago = month_start - timedelta(days=90)
    past_records = BudgetRecord.objects.filter(user=request.user, date__lt=month_start, date__gte=three_months_ago, spending_type=BudgetRecord.Type.EXPENSE)
    avg_past_spending = (past_records.aggregate(Sum('amount'))['amount__sum'] or 0) / 3
    spike_warning = avg_past_spending > 0 and expense > (avg_past_spending * 2)

    limits_data = []
    budget_warnings = []
    for cat in categories.exclude(classification='INCOME'):
        limit_obj, _ = CategoryLimit.objects.get_or_create(user=request.user, category=cat, month=month_start)
        spent = month_records.filter(category=cat, spending_type=BudgetRecord.Type.EXPENSE).aggregate(Sum('amount'))['amount__sum'] or 0
        percent = (spent / limit_obj.limit_amount * 100) if limit_obj.limit_amount > 0 else (100 if spent > 0 else 0)
        
        if percent >= 80 and limit_obj.limit_amount > 0:
            budget_warnings.append({'category': cat.name, 'percent': round(percent, 1), 'is_over': percent >= 100})
        limits_data.append({'category': cat, 'limit': limit_obj.limit_amount, 'spent': spent, 'percent': min(percent, 100), 'id': limit_obj.id})

    weekly_recap = None
    if today.weekday() == 0:
        last_week_start, last_week_end = today - timedelta(days=7), today - timedelta(days=1)
        last_week_records = BudgetRecord.objects.filter(user=request.user, date__range=[last_week_start, last_week_end], spending_type=BudgetRecord.Type.EXPENSE)
        last_week_total = last_week_records.aggregate(Sum('amount'))['amount__sum'] or 0
        top_cat_raw = last_week_records.values('category__name').annotate(total=Sum('amount')).order_by('-total').first()
        from apps.account.models import UserBadge
        new_badges = UserBadge.objects.filter(user=request.user, earned_at__date__range=[last_week_start, last_week_end]).select_related('badge')
        weekly_recap = {
            'total_spend': last_week_total, 'top_category': top_cat_raw['category__name'] if top_cat_raw else "None",
            'streak': profile.current_streak, 'new_badges': new_badges, 'start_date': last_week_start, 'end_date': last_week_end
        }

    context = {
        'total_income': income, 'total_expense': expense, 'balance': balance,
        'budget_remaining': budget_remaining, 'budget_percent': budget_percent, 'total_budget': total_available_budget,
        'base_budget': profile.budget, 'cat_labels_json': json.dumps(cat_labels), 'cat_data_json': json.dumps(cat_data),
        'nws_labels_json': json.dumps(nws_labels), 'nws_data_json': json.dumps(nws_data), 'nws_percents': nws_percents,
        'daily_labels_json': json.dumps(daily_labels), 'daily_data_json': json.dumps(daily_data),
        'categories': categories.exclude(classification='INCOME'), 'recent_records': month_records.order_by('-date', '-created_at')[:10],
        'now': today, 'daily_burn_rate': round(daily_burn_rate, 2), 'runway_days': int(runway_days),
        'runway_is_low': runway_is_low, 'spike_warning': spike_warning, 'avg_past_spending': round(avg_past_spending, 2), 
        'limits': limits_data, 'budget_warnings': budget_warnings, 'weekly_recap': weekly_recap, 'display_streak': display_streak,
    }
    return render(request, 'tracker/dashboard.html', context)

@login_required
def add_record(request):
    if request.method == "POST":
        spending_type = request.POST.get('type')
        category_id = request.POST.get('category')
        amount = request.POST.get('amount')
        
        # Basic validation
        if not amount or float(amount) <= 0:
            return HttpResponse("Invalid amount", status=400)

        if spending_type == 'INCOME':
            category, _ = Category.objects.get_or_create(name="Income", classification='INCOME')
        else:
            if not category_id:
                return HttpResponse("Category required for expenses", status=400)
            category = get_object_or_404(Category, id=category_id)
            
        BudgetRecord.objects.create(
            user=request.user, spending_type=spending_type,
            category=category, amount=amount,
            note=request.POST.get('note'), date=request.POST.get('date') or date.today()
        )
        update_user_gamification(request.user)
        return HttpResponse("", headers={"HX-Trigger": "recordAdded"})
    return render(request, 'tracker/partials/add_record_form.html', {
        'categories': Category.objects.exclude(classification='INCOME'), 'today': date.today()
    })

@login_required
def delete_record(request, record_id):
    record = get_object_or_404(BudgetRecord, id=record_id, user=request.user)
    if request.method == "POST":
        record.delete()
        return HttpResponse("", headers={"HX-Trigger": "recordAdded"})
    return HttpResponse(status=405)

@login_required
def edit_record(request, record_id):
    record = get_object_or_404(BudgetRecord, id=record_id, user=request.user)
    if request.method == "POST":
        spending_type = request.POST.get('type')
        amount = request.POST.get('amount')
        
        if not amount or float(amount) <= 0:
            return HttpResponse("Invalid amount", status=400)

        if spending_type == 'INCOME':
            category, _ = Category.objects.get_or_create(name="Income", classification='INCOME')
        else:
            category = get_object_or_404(Category, id=request.POST.get('category'))
        
        record.amount, record.spending_type, record.category = amount, spending_type, category
        record.date, record.note = request.POST.get('date'), request.POST.get('note')
        record.save()
        return HttpResponse("", headers={"HX-Trigger": "recordAdded"})
    return render(request, 'tracker/partials/edit_record_form.html', {
        'record': record, 'categories': Category.objects.exclude(classification='INCOME')
    })

@login_required
def record_list(request):
    records = BudgetRecord.objects.filter(user=request.user).select_related('category')
    search_query = request.GET.get('search')
    start_date, end_date = request.GET.get('start_date'), request.GET.get('end_date')
    category_id, spending_type = request.GET.get('category'), request.GET.get('type')
    if search_query: records = records.filter(Q(note__icontains=search_query) | Q(category__name__icontains=search_query))
    if start_date: records = records.filter(date__gte=start_date)
    if end_date: records = records.filter(date__lte=end_date)
    if category_id: records = records.filter(category_id=category_id)
    if spending_type: records = records.filter(spending_type=spending_type)
    context = {
        'records': records.order_by('-date', '-created_at'),
        'categories': Category.objects.all(),
        'types': BudgetRecord.Type.choices
    }
    if request.headers.get('HX-Request'): return render(request, 'tracker/partials/record_list_table.html', context)
    return render(request, 'tracker/record_list.html', context)

@login_required
def update_limit(request, limit_id):
    limit_obj = get_object_or_404(CategoryLimit, id=limit_id, user=request.user)
    profile = request.user.userprofile
    income, _, _ = get_monthly_summary(request.user, limit_obj.month.year, limit_obj.month.month)
    total_available = profile.budget + income
    
    error = None
    if request.method == "POST":
        try:
            new_limit = float(request.POST.get('limit_amount', 0))
            other_limits_sum = CategoryLimit.objects.filter(user=request.user, month=limit_obj.month).exclude(id=limit_id).aggregate(Sum('limit_amount'))['limit_amount__sum'] or 0
            
            if (other_limits_sum + new_limit) > total_available:
                error = f"Total limits cannot exceed your monthly budget (₱{total_available})"
            else:
                limit_obj.limit_amount = new_limit
                limit_obj.save()
                if request.headers.get('HX-Request'): 
                    return HttpResponse(f"₱{new_limit}", headers={"HX-Trigger": "recordAdded"})
                return redirect('manage_budgets')
        except (ValueError, TypeError):
            error = "Invalid limit amount"

    if error and request.headers.get('HX-Request'):
         return HttpResponse(f"<div hx-get=\"{reverse_lazy('update_limit', kwargs={'limit_id': limit_id})}\" hx-trigger=\"click\" class=\"cursor-pointer text-red-500 text-[10px] font-bold uppercase tracking-tighter\">{error}</div>", headers={"HX-Trigger": "allocationError"})

    return render(request, 'tracker/partials/limit_edit_form.html', {'limit': limit_obj, 'error': error})

@login_required
def category_limits(request):
    """
    Partial view for category limits progress bars.
    """
    today = date.today()
    month_start = today.replace(day=1)
    categories = Category.objects.exclude(classification='INCOME')
    month_records = BudgetRecord.objects.filter(user=request.user, date__year=today.year, date__month=today.month).select_related('category')
    
    limits_data = []
    for cat in categories:
        limit_obj, _ = CategoryLimit.objects.get_or_create(user=request.user, category=cat, month=month_start)
        spent = month_records.filter(category=cat, spending_type=BudgetRecord.Type.EXPENSE).aggregate(Sum('amount'))['amount__sum'] or 0
        percent = (spent / limit_obj.limit_amount * 100) if limit_obj.limit_amount > 0 else (100 if spent > 0 else 0)
        limits_data.append({'category': cat, 'limit': limit_obj.limit_amount, 'spent': spent, 'percent': min(percent, 100), 'id': limit_obj.id})
    
    return render(request, 'tracker/partials/category_limits.html', {'limits': limits_data})

@login_required
def manage_budgets(request):
    today = date.today()
    month_start = today.replace(day=1)
    profile = request.user.userprofile
    income, _, _ = get_monthly_summary(request.user, today.year, today.month)
    total_available = profile.budget + income
    categories = Category.objects.exclude(classification='INCOME')
    limits = [CategoryLimit.objects.get_or_create(user=request.user, category=cat, month=month_start)[0] for cat in categories]
    total_allocated = sum(l.limit_amount for l in limits)
    context = {
        'limits': limits, 'total_budget': total_available, 'total_allocated': total_allocated,
        'remaining_to_allocate': total_available - total_allocated,
        'allocation_percent': min((total_allocated / total_available * 100), 100) if total_available > 0 else 0
    }
    return render(request, 'tracker/manage_budgets.html', context)
