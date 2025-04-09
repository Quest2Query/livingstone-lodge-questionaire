from django.contrib import admin
from django.db.models import Count, Q
from .models import Guest, SatisfactionResponse, StayPurpose, AdditionalComment

class SatisfactionResponseInline(admin.TabularInline):
    model = SatisfactionResponse
    extra = 0

class StayPurposeInline(admin.TabularInline):
    model = StayPurpose
    extra = 0

class AdditionalCommentInline(admin.TabularInline):
    model = AdditionalComment
    extra = 0


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'room_number', 'length_of_stay', 'date_submitted')
    search_fields = ('name', 'room_number')
    list_filter = ('gender', 'length_of_stay', 'date_submitted')
    inlines = [SatisfactionResponseInline, StayPurposeInline, AdditionalCommentInline]

    def satisfaction_summary(self):
        """
        Generates the percentage summary of satisfaction ratings for all questions.
        """
        from django.utils.timezone import now
        from django.db.models import Count

        current_month = now().month
        current_year = now().year

        # Get responses for the current month
        total_responses = SatisfactionResponse.objects.filter(
            guest__date_submitted__month=current_month,
            guest__date_submitted__year=current_year
        ).count()

        if total_responses == 0:
            return "No responses yet"

        # Count each rating
        ratings_count = SatisfactionResponse.objects.filter(
            guest__date_submitted__month=current_month,
            guest__date_submitted__year=current_year
        ).aggregate(
            happy=Count('rating', filter=Q(rating='happy')),
            neutral=Count('rating', filter=Q(rating='neutral')),
            sad=Count('rating', filter=Q(rating='sad'))
        )

        happy_pct = (ratings_count['happy'] / total_responses) * 100 if ratings_count['happy'] else 0
        neutral_pct = (ratings_count['neutral'] / total_responses) * 100 if ratings_count['neutral'] else 0
        sad_pct = (ratings_count['sad'] / total_responses) * 100 if ratings_count['sad'] else 0

        return f"😊 {happy_pct:.1f}% | 😐 {neutral_pct:.1f}% | 😞 {sad_pct:.1f}%"

    def changelist_view(self, request, extra_context=None):
        """
        Adds the satisfaction summary to the admin panel.
        """
        extra_context = extra_context or {}
        extra_context['satisfaction_summary'] = self.satisfaction_summary()
        return super().changelist_view(request, extra_context=extra_context)

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)  # Optional: For custom styling
        }

admin.site.site_header = "Questionnaire Admin"
admin.site.site_title = "Questionnaire Admin Portal"
admin.site.index_title = "Welcome to the Guest Questionnaire Management"
