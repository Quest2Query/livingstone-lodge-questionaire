from django.db import models
from django.utils import timezone

class Guest(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    room_number = models.CharField(max_length=10)
    length_of_stay = models.CharField(
        max_length=20,
        choices=[
            ('1 Night', '1 Night'),
            ('2-5 Nights', '2-5 Nights'),
            ('6+ Nights', '6 or More Nights'),
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    date_submitted = models.DateField(default=timezone.now)  # NEW FIELD for admin grouping

    def __str__(self):
        return f"{self.name} - Room {self.room_number}"

class SatisfactionQuestion(models.Model):
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text

class SatisfactionResponse(models.Model):
    RATING_CHOICES = [
        ('happy', '😊'),
        ('neutral', '😐'),
        ('sad', '😞'),
    ]

    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='satisfaction_responses')
    question = models.ForeignKey(SatisfactionQuestion, on_delete=models.CASCADE)
    rating = models.CharField(max_length=10, choices=RATING_CHOICES)

    def __str__(self):
        return f"{self.guest.name} - {self.question.text} - {self.rating}"

class StayPurpose(models.Model):
    PURPOSE_CHOICES = [
        ('Business', 'Business'),
        ('Tourist', 'Tourist'),
        ('Conference', 'Conference'),
        ('Visiting', 'Visiting'),
        ('Other', 'Other'),
    ]

    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='stay_purposes')
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)

    def __str__(self):
        return f"{self.guest.name} - {self.purpose}"

class AdditionalComment(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()

    def __str__(self):
        return f"Comment from {self.guest.name}"
