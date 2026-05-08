from google import genai
from google.genai import types
from django.conf import settings
from apps.tracker.models import BudgetRecord, CategoryLimit, Category
from apps.account.models import UserProfile
from datetime import date
from django.db.models import Sum, Q
from decouple import config
from .models import ChatMessage
import os

# Ultra-short hardcoded persona
SYSTEM_PERSONA = "Coach Gemini: Pro FinTrack advisor. Use 50/30/20 rule. Direct, data-first. No preambles."

def get_financial_context(user):
    """
    Optimized compact snapshot.
    """
    today = date.today()
    month_start = today.replace(day=1)
    profile = UserProfile.objects.get(user=user)
    records = BudgetRecord.objects.filter(user=user, date__year=today.year, date__month=today.month)
    
    aggregates = records.aggregate(
        inc=Sum('amount', filter=Q(spending_type=BudgetRecord.Type.INCOME)),
        exp=Sum('amount', filter=Q(spending_type=BudgetRecord.Type.EXPENSE))
    )
    inc, exp = aggregates['inc'] or 0, aggregates['exp'] or 0
    cat_spending = records.filter(spending_type=BudgetRecord.Type.EXPENSE).values('category_id').annotate(total=Sum('amount'))
    cat_map = {item['category_id']: item['total'] for item in cat_spending}

    cat_stats = []
    limits = CategoryLimit.objects.filter(user=user, month=month_start).select_related('category')
    for lim in limits:
        spent = cat_map.get(lim.category.id, 0)
        cat_stats.append(f"{lim.category.name[0:3]}:{spent}/{lim.limit_amount}")

    return f"U:{user.username}|B:{profile.budget}|I:{inc}|E:{exp}|S:{profile.current_streak}|C:{','.join(cat_stats)}"

def get_coach_response(user, user_message):
    """
    Chatbot logic with rate-limit handling and minimal history.
    """
    client = genai.Client(api_key=config('GEMINI_API_KEY'))
    
    # Save user message immediately
    ChatMessage.objects.create(user=user, role="user", content=user_message)
    
    # Get minimal history (Last 4 messages) for maximum speed and lower rate-limit impact
    history_objs = ChatMessage.objects.filter(user=user).order_by('-created_at')[1:5]
    history = [types.Content(role=msg.role, parts=[types.Part.from_text(text=msg.content)]) for msg in reversed(history_objs)]

    system_instruction = f"{SYSTEM_PERSONA}\nDATA: {get_financial_context(user)}\nRULES: ULTRA-CONCISE. 1-2 sentences max."

    try:
        response = client.models.generate_content(
            model="models/gemini-3-flash-preview",
            contents=history + [types.Content(role="user", parts=[types.Part.from_text(text=user_message)])],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.6,
                max_output_tokens=150,
            )
        )
        
        ai_content = response.text or "I'm looking at your data. Ask me something specific!"
        ChatMessage.objects.create(user=user, role="model", content=ai_content)
        return ai_content
        
    except Exception as e:
        error_str = str(e).upper()
        if "429" in error_str or "QUOTA" in error_str:
            ai_content = "Coach is a bit overwhelmed! Please wait 60 seconds before your next question."
        elif "401" in error_str or "API_KEY" in error_str:
            ai_content = "Check your GEMINI_API_KEY in the .env file."
        else:
            ai_content = f"Coach is processing data. (Error: {str(e)[:30]})"
            
        ChatMessage.objects.create(user=user, role="model", content=ai_content)
        return ai_content
