from django import forms
from .models import UserInput
from .models import Quote

class UserInputForm(forms.ModelForm):
    # Add custom labels for fields
    read_bible = forms.BooleanField(
        required=False,
        label='Bible Reading',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    prayer_god = forms.BooleanField(
        required=False,
        label='Prayer for World Peace and Personal Necessities',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    exercised_or_played = forms.BooleanField(
        required=False,
        label='Exercise or Playing',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    book_reading = forms.BooleanField(
        required=False,
        label='Book Reading',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    studying_machine_learning = forms.BooleanField(
        required=False,
        label='Studying Machine Learning',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    maintained_purity = forms.BooleanField(
        required=False,
        label='Maintained Purity',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    cultivated_relationships = forms.BooleanField(
        required=False,
        label='Cultivating Good Relationships',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    woke_up_at_5am = forms.BooleanField(
        required=False,
        label='Woke up at 5:00 AM',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    healthy_eating = forms.BooleanField(
        required=False,
        label='Healthy Eating',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    hurt_someone = forms.BooleanField(
        required=False,
        label='Hurt Someone',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    wasted_time = forms.BooleanField(
        required=False,
        label='Wasted Time',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    loved_someone = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter name of someone you loved today',
            'autocomplete': 'off',
            'pattern': '[A-Za-z ]+',  # Only allow letters and spaces
            'title': 'Please enter only letters and spaces'
        })
    )
    
    daily_summary = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Share something nice you did today...',
            'rows': 4,
            'style': 'resize: none;',
            'minlength': '10',  # Minimum length requirement
        })
    )
    
    class Meta:
        model = UserInput
        fields = [
            'read_bible', 
            'prayer_god', 
            'exercised_or_played', 
            'book_reading', 
            'studying_machine_learning', 
            'maintained_purity', 
            'cultivated_relationships', 
            'woke_up_at_5am', 
            'healthy_eating', 
            'hurt_someone', 
            'wasted_time', 
            'loved_someone', 
            'daily_summary'
        ]
        


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['text']