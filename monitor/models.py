"""
Models for the monitor app.

This app is used to monitor daily activities and habits.
"""

from django.db import models


class UserInput(models.Model):
    """
    Model for storing daily user input.

    The model contains fields for storing the date and various habits
    such as reading the bible, praying, exercising, etc. It also has
    fields for storing the name of someone the user loved that day and
    a daily summary.
    """
    date = models.DateField(auto_now_add=True)

    # Boolean fields
    read_bible = models.BooleanField(default=False)
    prayer_god = models.BooleanField(default=False)
    exercised_or_played = models.BooleanField(default=False)
    book_reading = models.BooleanField(default=False)
    studying_machine_learning = models.BooleanField(default=False)
    maintained_purity = models.BooleanField(default=False)
    cultivated_relationships = models.BooleanField(default=False)
    woke_up_at_5am = models.BooleanField(default=False)
    healthy_eating = models.BooleanField(default=False)
    hurt_someone = models.BooleanField(default=False)
    wasted_time = models.BooleanField(default=False)

    # Char and text fields
    loved_someone = models.CharField(max_length=100, help_text="Name of someone you loved today.")
    daily_summary = models.TextField(max_length=500, help_text="A short summary of your day.")
    

    def __str__(self):
        """Return a string representation of the object."""
        return f"{self.date}: {self.loved_someone}"


class Quote(models.Model):
    """
    Model for storing quotes.

    The model contains a single field for storing the text of the quote.
    """
    text = models.TextField(max_length=3000)

    
    def __str__(self):
        """Return a string representation of the object."""
        return self.text[:50]  # Show first 50 characters of the quote in admin


class CalendarTask(models.Model):
    """
    Model for storing calendar tasks.

    The model contains fields for storing the date, name, and type of the task.
    The type field is a choice field with options for normal and day tasks.
    """
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
    
    priority = models.CharField(max_length=50, default='important', choices=[('high', 'Highly Important'), ('medium', 'Medium Important'), ('important', 'Important')])

    def __str__(self):
        """Return a string representation of the object."""
        return f"{self.name}: {self.date}"


class TodoTask(models.Model):
    """
    Model for storing todo tasks.

    The model contains a single field for storing the name of the task.
    """
    task_name = models.CharField(max_length=255)
        
    def __str__(self):
        """Return a string representation of the object."""
        return self.task_name



