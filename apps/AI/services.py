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
SYSTEM_PERSONA = "Minto: Pro FinTrack advisor. Use 50/30/20 rule. Direct, data-first. No preambles."

def get_financial_context(user, query=""):
    """
    RAG-style context retrieval:
    1. Fetches current month aggregates.
    2. Searches for specific transactions related to the query.
    3. Fetches user profile stats.
    """
    today = date.today()
    month_start = today.replace(day=1)
    profile = UserProfile.objects.get(user=user)
    
    # Base Month Aggregates
    records = BudgetRecord.objects.filter(user=user, date__year=today.year, date__month=today.month)
    aggregates = records.aggregate(
        inc=Sum('amount', filter=Q(spending_type=BudgetRecord.Type.INCOME)),
        exp=Sum('amount', filter=Q(spending_type=BudgetRecord.Type.EXPENSE))
    )
    inc, exp = aggregates['inc'] or 0, aggregates['exp'] or 0

    # Retrieval Step: Search for keywords in notes or categories
    relevant_search = Q()
    keywords = query.lower().split()
    for word in keywords:
        if len(word) > 2: # Ignore short words
            relevant_search |= Q(note__icontains=word) | Q(category__name__icontains=word)
    
    retrieved_records = []
    if relevant_search:
        # Get up to 5 most recent relevant transactions from any date
        search_results = BudgetRecord.objects.filter(user=user).filter(relevant_search).select_related('category').order_by('-date')[:5]
        for r in search_results:
            retrieved_records.append(f"{r.date}:{r.category.name}={r.amount}({r.note or ''})")

    # Category Limits
    cat_stats = []
    limits = CategoryLimit.objects.filter(user=user, month=month_start).select_related('category')
    cat_spending = records.filter(spending_type=BudgetRecord.Type.EXPENSE).values('category_id').annotate(total=Sum('amount'))
    cat_map = {item['category_id']: item['total'] for item in cat_spending}
    
    for lim in limits:
        spent = cat_map.get(lim.category.id, 0)
        cat_stats.append(f"{lim.category.name[0:3]}:{spent}/{lim.limit_amount}")

    context_parts = [
        f"U:{user.username}",
        f"B:{profile.budget}",
        f"MONTH_I:{inc}|E:{exp}",
        f"STREAK:{profile.current_streak}",
        f"LIMITS:{','.join(cat_stats)}",
    ]
    
    if retrieved_records:
        context_parts.append(f"RETRIEVED_RECORDS:{'|'.join(retrieved_records)}")

    return "|".join(context_parts)

def get_coach_response(user, user_message):
    """
    Chatbot logic with retrieval-augmented context.
    Supports /help command for guidance.
    """
    # 1. Handle deterministic /help command
    if user_message.strip().lower() == "/help":
        help_text = (
            "**Minto Help**\n\n"
            "I can analyze your finances and give advice. Try asking:\n"
            "- *'How much did I spend on Food this month?'*\n"
            "- *'Am I over budget?'*\n"
            "- *'Find my transactions related to pizza'*\n"
            "- *'What is my current streak?'*\n\n"
            "Type **Reset** to clear our history."
        )
        ChatMessage.objects.create(user=user, role="model", content=help_text)
        return help_text

    client = genai.Client(api_key=config('GEMINI_API_KEY'))
    
    # Save user message immediately
    ChatMessage.objects.create(user=user, role="user", content=user_message)
    
    # Get minimal history
    history_objs = ChatMessage.objects.filter(user=user).order_by('-created_at')[1:5]
    history = [types.Content(role=msg.role, parts=[types.Part.from_text(text=msg.content)]) for msg in reversed(history_objs)]

    # Retrieval-Augmented Generation: Get context based on current query
    context = get_financial_context(user, query=user_message)
    
    system_instruction = f"{SYSTEM_PERSONA}\nCONTEXT_DATA: {context}\nRULES: Direct and professional. Use the RETRIEVED_RECORDS to provide specific details. Be concise but ensure the answer is complete. No length limit if details are needed."

    try:
        response = client.models.generate_content(
            model="models/gemini-3-flash-preview",
            contents=history + [types.Content(role="user", parts=[types.Part.from_text(text=user_message)])],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.6,
                max_output_tokens=1500,
            )
        )
        
        ai_content = response.text or "I'm looking at your data. Ask me something specific!"
        ChatMessage.objects.create(user=user, role="model", content=ai_content)
        return ai_content
        
    except Exception as e:
        error_str = str(e).upper()
        if "429" in error_str or "QUOTA" in error_str:
            ai_content = "Minto is a bit overwhelmed! Please wait 60 seconds before your next question."
        elif "401" in error_str or "API_KEY" in error_str:
            ai_content = "Check your GEMINI_API_KEY in the .env file."
        else:
            ai_content = f"Minto is processing data. (Error: {str(e)[:30]})"
            
        ChatMessage.objects.create(user=user, role="model", content=ai_content)
        return ai_content
