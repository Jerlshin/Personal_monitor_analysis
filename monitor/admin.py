# monitor/admin.py
from django.contrib import admin
from .models import UserInput, CalendarTask, TodoTask, Quote

# Registering UserInput model with custom configuration
@admin.register(UserInput)
class UserInputAdmin(admin.ModelAdmin):
    # Displaying more detailed information in the list view
    list_display = [
        'date', 'read_bible', 'prayer_god', 'exercised_or_played', 'book_reading',
        'studying_machine_learning', 'maintained_purity', 'cultivated_relationships',
        'woke_up_at_5am', 'healthy_eating', 'hurt_someone', 'wasted_time', 'loved_someone'
    ]
    # Adding filters for easy categorization
    list_filter = [
        'read_bible', 'prayer_god', 'exercised_or_played', 'book_reading',
        'studying_machine_learning', 'maintained_purity', 'cultivated_relationships',
        'woke_up_at_5am', 'healthy_eating', 'hurt_someone', 'wasted_time'
    ]
    # Enabling search for specific fields
    search_fields = ['loved_someone', 'daily_summary']
    
    # Exclude 'date' field from the form, as it's not editable
    exclude = ['date']

    # Organizing the form in a more user-friendly way in the admin form view
    fieldsets = (
        (None, {
            'fields': ('loved_someone', 'daily_summary')
        }),
        ('Habits and Activities', {
            'fields': (
                'read_bible', 'prayer_god', 'exercised_or_played', 'book_reading',
                'studying_machine_learning', 'maintained_purity', 'cultivated_relationships',
                'woke_up_at_5am', 'healthy_eating', 'hurt_someone', 'wasted_time'
            ),
            'classes': ('collapse',),  # To make the section collapsible
        }),
    )

    # Displaying the string representation of the object in the list view
    def __str__(self):
        return f"{self.date}: {self.loved_someone}"
# Registering CalendarTask model with custom configuration
@admin.register(CalendarTask)
class CalendarTaskAdmin(admin.ModelAdmin):
    list_display = ['date', 'name', 'task_type', 'priority']
    list_filter = ['task_type', 'priority']
    search_fields = ['name']

# Registering TodoTask model with custom configuration
@admin.register(TodoTask)
class TodoTaskAdmin(admin.ModelAdmin):
    list_display = ['task_name']
    search_fields = ['task_name']

# Registering Quote model with custom configuration
@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ['text']  # Display only the text field for quotes
    search_fields = ['text']  # Enable search on quote text
