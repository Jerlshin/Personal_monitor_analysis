from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Sum, Count, Q, Max
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import openpyxl
from openpyxl.utils import get_column_letter
import json
from datetime import datetime, timedelta
import calendar

# DRF Imports
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from .serializers import CalendarTaskSerializer, TodoTaskSerializer

# Models and Forms
from .models import Quote, CalendarTask, TodoTask, Plan, Branch, Habit, DailyEntry, HabitLog
from .forms import QuoteForm, PlanForm, BranchForm, HabitForm, DailyEntryForm

# --- Authentication Views ---
# (Login/Logout views remain the same)
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        STATIC_USERNAME = 'jerlshin'
        STATIC_PASSWORD = 'Imfreaked@008'
        if username == STATIC_USERNAME and password == STATIC_PASSWORD:
            user, created = User.objects.get_or_create(username=STATIC_USERNAME)
            if created or not user.has_usable_password():
                user.set_unusable_password()
                user.save()
            if user:
                 login(request, user)
                 return redirect('home')
        else:
            user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'monitor/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# --- Home & Quote Views ---
@login_required
def home_view(request):
    quotes = Quote.objects.all().order_by('order')
    form = QuoteForm()
    if request.method == "POST":
        form = QuoteForm(request.POST)
        if form.is_valid():
            last_order = Quote.objects.aggregate(max_order=Max('order'))['max_order']
            form.instance.order = (last_order or 0) + 1
            form.save()
            return redirect('home')
    return render(request, 'monitor/home.html', {'quotes': quotes, 'form': form})

@csrf_exempt
def delete_quote(request, id):
    if request.method == "POST":
        try:
            quote = Quote.objects.get(id=id)
            quote.delete()
            return JsonResponse({"success": True})
        except Quote.DoesNotExist:
            return JsonResponse({"success": False, "error": "Quote not found"})
    return JsonResponse({"success": False, "error": "Invalid request method"})

# --- Dynamic Data Management Views ---
@login_required
def habit_list(request):
    habits = Habit.objects.all().order_by('order')
    quotes = Quote.objects.all().order_by('order')
    return render(request, 'monitor/habit_list.html', {
        'habits': habits, 
        'quotes': quotes,
        'habit_form': HabitForm(),
        'quote_form': QuoteForm()
    })

@login_required
def habit_create(request):
    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('habit_list')
    return redirect('habit_list')

@login_required
def habit_update(request, pk):
    habit = get_object_or_404(Habit, pk=pk)
    if request.method == 'POST':
        form = HabitForm(request.POST, instance=habit)
        if form.is_valid():
            form.save()
            return redirect('habit_list')
    else:
        form = HabitForm(instance=habit)
    return render(request, 'monitor/habit_form.html', {'form': form, 'title': 'Edit Habit'})

@login_required
def habit_delete(request, pk):
    habit = get_object_or_404(Habit, pk=pk)
    if request.method == 'POST':
        habit.delete()
    return redirect('habit_list')

@login_required
def quote_create_manage(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            last_order = Quote.objects.aggregate(max_order=Max('order'))['max_order']
            form.instance.order = (last_order or 0) + 1
            form.save()
            return redirect('habit_list')
    return redirect('habit_list')

@login_required
def quote_update_manage(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    if request.method == 'POST':
        form = QuoteForm(request.POST, instance=quote)
        if form.is_valid():
            form.save()
            return redirect('habit_list')
    else:
        form = QuoteForm(instance=quote)
    return render(request, 'monitor/quote_form.html', {'form': form, 'title': 'Edit Quote'})

@login_required
def quote_delete_manage(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    if request.method == 'POST':
        quote.delete()
    return redirect('habit_list')

@login_required
@csrf_exempt
def reorder_quotes(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            for index, quote_id in enumerate(data.get('order', [])):
                Quote.objects.filter(id=quote_id).update(order=index)
            return JsonResponse({'success': True})
        except Exception as e: return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})

# --- Input View ---
@login_required
def input_view(request):
    active_habits = Habit.objects.filter(is_active=True).order_by('order')
    current_date = timezone.now().date()

    if request.method == 'POST':
        form = DailyEntryForm(request.POST)
        if form.is_valid():
            daily_entry = form.save(commit=False)
            daily_entry.date = current_date
            daily_entry.save()

            for habit in active_habits:
                checkbox_name = f"habit_{habit.id}"
                is_completed = request.POST.get(checkbox_name) == 'on'
                HabitLog.objects.create(entry=daily_entry, habit=habit, completed=is_completed)
            
            return redirect('home')
    else:
        form = DailyEntryForm()

    return render(request, 'monitor/input.html', {
        'form': form, 
        'habits': active_habits,
        'current_date': current_date
    })

# --- Chart View ---
@login_required
def chart_view(request):
    entries = DailyEntry.objects.all().order_by('date')
    line_labels = []
    cumulative_scores = []
    current_total = 0

    for entry in entries:
        line_labels.append(entry.date.strftime('%Y-%m-%d'))
        day_score = 0
        logs = entry.habit_logs.all()
        
        for log in logs:
            if log.completed:
                day_score += log.habit.positive_score + log.habit.negative_score
        
        current_total += day_score
        cumulative_scores.append(current_total)

    line_chart_data = {
        'labels': line_labels,
        'cumulative_score': cumulative_scores
    }

    all_habits = Habit.objects.all()
    bar_labels = []
    bar_values = []

    for habit in all_habits:
        bar_labels.append(habit.name)
        checked_logs_count = HabitLog.objects.filter(habit=habit, completed=True).count()
        total_impact = checked_logs_count * (habit.positive_score + habit.negative_score)
        bar_values.append(total_impact)

    bar_chart_data = {
        'labels': bar_labels,
        'values': bar_values
    }

    return render(request, 'monitor/chart.html', {
        'line_chart_data': line_chart_data,
        'bar_chart_data': bar_chart_data,
    })

# --- NEW VIEW DATA FUNCTIONALITY ---

@login_required
def view_data(request):
    # 1. Period Selection Logic
    today = timezone.now().date()
    selected_month = int(request.GET.get('month', today.month))
    selected_year = int(request.GET.get('year', today.year))
    
    # Construct date range
    _, num_days = calendar.monthrange(selected_year, selected_month)
    start_date = datetime(selected_year, selected_month, 1).date()
    end_date = datetime(selected_year, selected_month, num_days).date()

    # 2. Fetch Data
    entries = DailyEntry.objects.filter(date__range=[start_date, end_date]).order_by('date')
    all_habits = Habit.objects.all().order_by('order')
    
    # 3. Filter Selected Habits (for display)
    # If specific habits are selected in GET param, use those. Else default to all.
    selected_habit_ids = request.GET.getlist('habits')
    if selected_habit_ids:
        selected_habit_ids = [int(id) for id in selected_habit_ids]
        display_habits = all_habits.filter(id__in=selected_habit_ids)
    else:
        display_habits = all_habits
        selected_habit_ids = [h.id for h in all_habits] # Select all by default for UI

    # 4. Prepare Habit Data for Grid/Plot
    # Structure: { date: { habit_name: status_bool, ... }, ... }
    habit_data = []
    for entry in entries:
        day_data = {'date': entry.date.strftime('%Y-%m-%d')}
        for habit in display_habits:
            log = entry.habit_logs.filter(habit=habit).first()
            day_data[habit.name] = 1 if (log and log.completed) else 0
        habit_data.append(day_data)

    # 5. Process "Loved Someone" Data
    # Normalize: lowercase, strip spaces
    loved_counts = {}
    for entry in entries:
        if entry.loved_someone:
            name = entry.loved_someone.lower().strip()
            if name:
                loved_counts[name] = loved_counts.get(name, 0) + 1
    
    # Sort by count desc
    sorted_loved = sorted(loved_counts.items(), key=lambda item: item[1], reverse=True)
    loved_labels = [item[0].title() for item in sorted_loved] # Title case for display
    loved_values = [item[1] for item in sorted_loved]

    context = {
        'entries': entries, # For journal view
        'all_habits': all_habits,
        'display_habits': display_habits,
        'selected_habit_ids': selected_habit_ids,
        'habit_data_json': json.dumps(habit_data), # For JS Charts
        'loved_labels': json.dumps(loved_labels),
        'loved_values': json.dumps(loved_values),
        'years': range(today.year - 5, today.year + 5),
        'months': range(1, 13),
        'selected_year': selected_year,
        'selected_month': selected_month,
        'month_name': calendar.month_name[selected_month]
    }
    return render(request, 'monitor/view_data.html', context)


# --- Legacy Export (Kept as fallback if needed, not linked) ---
@login_required
def export_to_excel_view(request):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "User Inputs"
    habits = list(Habit.objects.all().order_by('order'))
    headers = ['Date'] + [h.name for h in habits] + ['Loved Someone', 'Daily Summary']
    sheet.append(headers)
    entries = DailyEntry.objects.all().order_by('date')
    for entry in entries:
        row = [entry.date.strftime('%Y-%m-%d')]
        for habit in habits:
            log = HabitLog.objects.filter(entry=entry, habit=habit).first()
            row.append('Yes' if log and log.completed else 'No')
        row.extend([entry.loved_someone, entry.daily_summary])
        sheet.append(row)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="user_inputs.xlsx"'
    workbook.save(response)
    return response

# --- Other Existing Views ---
@login_required
def calendar_view(request): return render(request, 'monitor/calendar.html')
@login_required
def plan_ideas(request): return render(request, 'monitor/plan_ideas.html', {'plans': Plan.objects.all()})
class CalendarTaskViewSet(ModelViewSet): permission_classes = [AllowAny]; queryset = CalendarTask.objects.all(); serializer_class = CalendarTaskSerializer
class TodoTaskViewSet(ModelViewSet): queryset = TodoTask.objects.all(); serializer_class = TodoTaskSerializer; permission_classes = [AllowAny]
@csrf_exempt
def load_tasks(request):
    try: date = datetime.strptime(request.GET.get('date'), '%Y-%m-%d').date()
    except: return JsonResponse({'error': 'Invalid date'}, status=400)
    return JsonResponse([{'id': t.id, 'name': t.name, 'task_type': t.task_type, 'priority': t.priority, 'date': t.date.strftime('%Y-%m-%d')} for t in CalendarTask.objects.filter(date=date)], safe=False)

# API Stubs
@login_required
def add_plan_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            form = PlanForm(data)
            if form.is_valid():
                plan = form.save()
                return JsonResponse({'success': True, 'plan': {'id': plan.id, 'title': plan.title, 'description': plan.description}})
        except Exception as e: return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})
@login_required
def add_branch_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            plan = Plan.objects.get(id=data.get('plan_id'))
            branch = Branch.objects.create(plan=plan, name=data.get('branch_name'), notes=data.get('branch_notes'))
            return JsonResponse({'success': True, 'branch': {'id': branch.id, 'name': branch.name}})
        except Exception as e: return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})
@login_required
def delete_plan_api(request):
    if request.method == 'POST':
        try:
            Plan.objects.get(id=json.loads(request.body).get('plan_id')).delete()
            return JsonResponse({'success': True})
        except: return JsonResponse({'success': False})
    return JsonResponse({'success': False})
@login_required
def delete_branch_api(request):
    if request.method == 'POST':
        try:
            Branch.objects.get(id=json.loads(request.body).get('branch_id')).delete()
            return JsonResponse({'success': True})
        except: return JsonResponse({'success': False})
    return JsonResponse({'success': False})