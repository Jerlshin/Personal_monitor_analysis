from django.db import models

# --- Dynamic Habit System ---

class Habit(models.Model):
    """
    Defines a habit that can be tracked.
    Stores the scoring rules for this specific habit.
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    # Score added if the habit is marked as "Done" / True
    positive_score = models.IntegerField(default=1, help_text="Score added if this habit is completed (e.g., 1, 2).")
    # Score added (usually negative) if the habit is NOT done or marked True (depending on logic)
    # For "Bad Habits" (like Wasted Time), you might check the box to indicate you did it, 
    # so you might want a negative score here.
    negative_score = models.IntegerField(default=0, help_text="Score added if this habit is checked (for bad habits) or missed. Usually 0 or negative (e.g., -1).")
    
    is_active = models.BooleanField(default=True, help_text="Uncheck to hide this habit from new inputs without deleting old data.")
    order = models.IntegerField(default=0, help_text="Order to display in the form.")

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['order', 'name']

class DailyEntry(models.Model):
    """
    Replaces the old UserInput model.
    Stores the daily summary and metadata, but NOT the specific boolean habits.
    """
    date = models.DateField()
    loved_someone = models.CharField(max_length=100, blank=True, help_text="Name of someone you loved today.")
    daily_summary = models.TextField(blank=True, help_text="A short summary of your day.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Entry for {self.date}"
    
    class Meta:
        ordering = ['-date']

class HabitLog(models.Model):
    """
    Records the status of a single habit for a single day.
    """
    entry = models.ForeignKey(DailyEntry, on_delete=models.CASCADE, related_name='habit_logs')
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    def __str__(self):
        status = "Done" if self.completed else "Not Done"
        return f"{self.habit.name} - {self.entry.date}: {status}"

# --- Existing Models ---

class Quote(models.Model):
    text = models.TextField(max_length=3000)
    # Field to track the "sense" tick state (Green color)
    is_sensed = models.BooleanField(default=False) 
    # Field for manual ordering
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.text[:50]
    
    class Meta:
        ordering = ['order'] # Default ordering by the new order field

class CalendarTask(models.Model):
    date = models.DateField()
    name = models.CharField(max_length=255)
    task_type = models.CharField(
        max_length=50,
        choices=[('normal', 'Normal'), ('day', 'Day')],
    )
    priority = models.CharField(
        max_length=50,
        default='important',
        choices=[
            ('high', 'Highly Important'),
            ('medium', 'Medium Important'),
            ('important', 'Important'),
        ],
    )
    def __str__(self):
        return f"{self.name}: {self.date}"

class TodoTask(models.Model):
    task_name = models.CharField(max_length=255)
    def __str__(self):
        return self.task_name

class Plan(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title

class Branch(models.Model):
    plan = models.ForeignKey(Plan, related_name='branches', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name