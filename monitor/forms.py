from django import forms
from .models import Quote, Plan, Branch, Habit, DailyEntry

class DailyEntryForm(forms.ModelForm):
    loved_someone = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter name of someone you loved today',
            'autocomplete': 'off'
        })
    )
    
    daily_summary = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Share something about today...',
            'rows': 4,
            'style': 'resize: none;'
        })
    )

    class Meta:
        model = DailyEntry
        fields = ['loved_someone', 'daily_summary']

class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['name', 'description', 'positive_score', 'negative_score', 'is_active', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'positive_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'negative_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class QuoteForm(forms.ModelForm):
    is_sensed = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'sense-tick'})
    )
    
    # Explicitly set order to not required for forms, as it's handled programmatically or via drag-drop
    order = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Quote
        fields = ['text', 'is_sensed', 'order']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        
class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['title', 'description']

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['plan', 'name', 'notes']