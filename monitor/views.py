from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Sum, Count, Q, Max
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.conf import settings
from django.db import connections, DEFAULT_DB_ALIAS
from django.core.management import call_command
import openpyxl
import json
import os
from pathlib import Path
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

def settings_view(request):
    # Context variables
    account_exists = User.objects.exists()
    current_db_path = str(settings.DATABASES['default']['NAME'])
    
    # Flags for UI states
    setup_required = False 
    
    # Ensure directory exists
    db_folder = settings.BASE_DIR / 'user_databases'
    db_folder.mkdir(exist_ok=True)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        # ==========================================
        # 1. SWITCH DATABASE (File Upload)
        # ==========================================
        if action == 'switch_database':
            uploaded_file = request.FILES.get('db_file')
            
            if uploaded_file:
                filename = uploaded_file.name
                if not (filename.endswith('.sqlite3') or filename.endswith('.db')):
                    messages.error(request, "Invalid file type. Please select .sqlite3 or .db")
                    return redirect('settings')
                
                new_db_path = db_folder / filename
                
                # Save file
                try:
                    with open(new_db_path, 'wb+') as destination:
                        for chunk in uploaded_file.chunks():
                            destination.write(chunk)
                except Exception as e:
                    messages.error(request, f"Error saving file: {e}")
                    return redirect('settings')

                # Switch Config
                _switch_db_connection(request, new_db_path)
                
                # Immediate Logout for Switch
                logout(request)
                return redirect('login')
            else:
                messages.error(request, "Please upload a file to switch.")
                return redirect('settings')

        # ==========================================
        # 2. CREATE DATABASE (Step 1: Initialize)
        # ==========================================
        elif action == 'create_database':
            db_name = request.POST.get('new_db_name', '').strip()
            if not db_name:
                db_name = f"db_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            if not db_name.endswith('.sqlite3'):
                db_name += '.sqlite3'
                
            new_db_path = db_folder / db_name
            
            # Create/Switch Config
            success = _switch_db_connection(request, new_db_path)
            
            if success:
                # DO NOT LOGOUT YET. 
                # Render page with 'setup_required' flag to show the Admin Creation Modal
                setup_required = True
                messages.success(request, f"Database '{db_name}' created. Please set up the admin account.")
            else:
                return redirect('settings')

        # ==========================================
        # 3. SETUP NEW ADMIN (Step 2: Create User)
        # ==========================================
        elif action == 'setup_new_admin':
            username = request.POST.get('username')
            password = request.POST.get('password')
            confirm = request.POST.get('confirm_password')
            
            if password != confirm:
                messages.error(request, "Passwords do not match.")
                setup_required = True # Keep modal open
            else:
                try:
                    User.objects.create_user(username=username, password=password)
                    messages.success(request, "Admin account created successfully. Please login.")
                    logout(request)
                    return redirect('login')
                except Exception as e:
                    messages.error(request, f"Error creating user: {e}")
                    setup_required = True

        # ==========================================
        # 4. UPDATE PROFILE
        # ==========================================
        elif request.user.is_authenticated and action == 'update_profile':
            _handle_profile_update(request)
            return redirect('settings')

        # ==========================================
        # 5. GUEST ACTIONS (Register/Reset)
        # ==========================================
        elif not request.user.is_authenticated:
            _handle_guest_actions(request, account_exists, action)
            if action in ['register', 'reset_password']:
                # Redirect handled inside helper or fall through
                if not messages.get_messages(request):
                    return redirect('home') # Fallback success redirect

    return render(request, 'monitor/settings.html', {
        'account_exists': account_exists,
        'current_db_path': current_db_path,
        'setup_required': setup_required
    })

# --- Helper Functions ---

def _switch_db_connection(request, new_db_path):
    """Updates persistence, settings, closes connections, and migrates."""
    config_data = {'db_path': str(new_db_path.resolve())}
    config_path = settings.BASE_DIR / 'db_config.json'
    
    try:
        # Persist
        with open(config_path, 'w') as f:
            json.dump(config_data, f)
            
        # Switch Runtime
        old_db_name = settings.DATABASES['default']['NAME']
        settings.DATABASES['default']['NAME'] = new_db_path
        connections[DEFAULT_DB_ALIAS].close()
        
        # Migrate
        call_command('migrate', interactive=False)
        return True
        
    except Exception as e:
        # Revert
        settings.DATABASES['default']['NAME'] = old_db_name
        messages.error(request, f"Database switch failed: {e}")
        return False

def _handle_profile_update(request):
    new_username = request.POST.get('username')
    new_password = request.POST.get('new_password')
    confirm_password = request.POST.get('confirm_password')
    user = request.user
    
    if new_username and new_username != user.username:
        if User.objects.filter(username=new_username).exists():
            messages.error(request, 'Username taken.')
            return
        user.username = new_username
        messages.success(request, 'Username updated.')

    if new_password:
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return
        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Password updated.')
    else:
        user.save()

def _handle_guest_actions(request, account_exists, action):
    if action == 'register':
        if account_exists:
            messages.error(request, 'Registration disabled.')
            return
        # ... existing register logic ...
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')
        if password != confirm: 
            messages.error(request, 'Passwords mismatch.')
            return
        if User.objects.filter(username=username).exists(): 
            messages.error(request, 'User exists.')
            return
        user = User.objects.create_user(username=username, password=password)
        login(request, user)

    elif action == 'reset_password':
        if not account_exists:
            messages.error(request, 'No account to reset.')
            return
        # ... existing reset logic ...
        target_user = request.POST.get('username')
        new_pass = request.POST.get('new_password')
        confirm = request.POST.get('confirm_password')
        try:
            u = User.objects.get(username=target_user)
            if new_pass != confirm:
                messages.error(request, 'Mismatch.')
                return
            u.set_password(new_pass)
            u.save()
            messages.success(request, 'Reset successful.')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')

# --- Unchanged Views ---
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

@login_required
def view_data(request):
    today = timezone.now().date()
    selected_month = int(request.GET.get('month', today.month))
    selected_year = int(request.GET.get('year', today.year))
    
    _, num_days = calendar.monthrange(selected_year, selected_month)
    start_date = datetime(selected_year, selected_month, 1).date()
    end_date = datetime(selected_year, selected_month, num_days).date()

    entries = DailyEntry.objects.filter(date__range=[start_date, end_date]).order_by('date')
    all_habits = Habit.objects.all().order_by('order')
    
    selected_habit_ids = request.GET.getlist('habits')
    if selected_habit_ids:
        selected_habit_ids = [int(id) for id in selected_habit_ids]
        display_habits = all_habits.filter(id__in=selected_habit_ids)
    else:
        display_habits = all_habits
        selected_habit_ids = [h.id for h in all_habits]

    habit_data = []
    for entry in entries:
        day_data = {'date': entry.date.strftime('%Y-%m-%d')}
        for habit in display_habits:
            log = entry.habit_logs.filter(habit=habit).first()
            day_data[habit.name] = 1 if (log and log.completed) else 0
        habit_data.append(day_data)

    loved_counts = {}
    for entry in entries:
        if entry.loved_someone:
            name = entry.loved_someone.lower().strip()
            if name:
                loved_counts[name] = loved_counts.get(name, 0) + 1
    
    sorted_loved = sorted(loved_counts.items(), key=lambda item: item[1], reverse=True)
    loved_labels = [item[0].title() for item in sorted_loved]
    loved_values = [item[1] for item in sorted_loved]

    context = {
        'entries': entries,
        'all_habits': all_habits,
        'display_habits': display_habits,
        'selected_habit_ids': selected_habit_ids,
        'habit_data_json': json.dumps(habit_data),
        'loved_labels': json.dumps(loved_labels),
        'loved_values': json.dumps(loved_values),
        'years': range(today.year - 5, today.year + 5),
        'months': range(1, 13),
        'selected_year': selected_year,
        'selected_month': selected_month,
        'month_name': calendar.month_name[selected_month]
    }
    return render(request, 'monitor/view_data.html', context)

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