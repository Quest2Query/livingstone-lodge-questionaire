from django import forms
from .models import Guest, SatisfactionResponse, StayPurpose, AdditionalComment

class GuestForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = ['name', 'gender', 'room_number', 'length_of_stay']

class SatisfactionResponseForm(forms.ModelForm):
    class Meta:
        model = SatisfactionResponse
        fields = ['question', 'rating']
        widgets = {
            'rating': forms.RadioSelect(choices=SatisfactionResponse.RATING_CHOICES)
        }

class StayPurposeForm(forms.ModelForm):
    class Meta:
        model = StayPurpose
        fields = ['purpose']

class AdditionalCommentForm(forms.ModelForm):
    class Meta:
        model = AdditionalComment
        fields = ['comment']


