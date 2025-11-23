from django.contrib import admin
from .models import DailyEntry, Habit, HabitLog, CalendarTask, TodoTask, Quote, Plan, Branch

# Registering the new Dynamic Models

@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ['name', 'positive_score', 'negative_score', 'is_active', 'order']
    list_editable = ['order', 'is_active']
    ordering = ['order']

# Allow viewing habit logs inside the Daily Entry view
class HabitLogInline(admin.TabularInline):
    model = HabitLog
    extra = 0

@admin.register(DailyEntry)
class DailyEntryAdmin(admin.ModelAdmin):
    list_display = ['date', 'loved_someone', 'created_at']
    search_fields = ['daily_summary', 'loved_someone']
    inlines = [HabitLogInline]

# --- Existing Models ---

@admin.register(CalendarTask)
class CalendarTaskAdmin(admin.ModelAdmin):
    list_display = ['date', 'name', 'task_type', 'priority']
    list_filter = ['task_type', 'priority']
    search_fields = ['name']

@admin.register(TodoTask)
class TodoTaskAdmin(admin.ModelAdmin):
    list_display = ['task_name']
    search_fields = ['task_name']

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ['text']
    search_fields = ['text']

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan', 'created_at']