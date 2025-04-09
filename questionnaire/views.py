from django.shortcuts import render, redirect, get_object_or_404
from .forms import GuestForm, SatisfactionResponseForm, StayPurposeForm, AdditionalCommentForm
from .models import Guest, SatisfactionQuestion, SatisfactionResponse
from django.contrib.auth.decorators import login_required


def questionnaire_view(request):
    if request.method == 'POST':
        guest_form = GuestForm(request.POST)
        stay_purpose_form = StayPurposeForm(request.POST)
        comment_form = AdditionalCommentForm(request.POST)

        if guest_form.is_valid():
            guest = guest_form.save()

            # Save stay purpose
            stay_purpose = stay_purpose_form.save(commit=False)
            stay_purpose.guest = guest
            stay_purpose.save()

            # Save additional comment
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.guest = guest
                comment.save()

            # Save satisfaction responses
            for question in SatisfactionQuestion.objects.all():
                rating = request.POST.get(f"rating_{question.id}")
                if rating:
                    SatisfactionResponse.objects.create(guest=guest, question=question, rating=rating)

            return redirect('thank_you')  # Redirect to a thank you page

    else:
        guest_form = GuestForm()
        stay_purpose_form = StayPurposeForm()
        comment_form = AdditionalCommentForm()
        satisfaction_questions = SatisfactionQuestion.objects.all()

    return render(request, 'questionnaire_form.html', {
        'guest_form': guest_form,
        'stay_purpose_form': stay_purpose_form,
        'comment_form': comment_form,
        'satisfaction_questions': satisfaction_questions,
    })


def thank_you_view(request):
    return render(request, 'thank_you.html')


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models.functions import TruncMonth
from django.db.models import Count
from .models import Guest
from django.contrib import messages

# Guest info view (protected)
@login_required
def guest_info(request):
    guests_by_month = (
        Guest.objects.annotate(month=TruncMonth('date_submitted'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('-month')
    )

    guests = Guest.objects.all().order_by('-date_submitted')  # Get all guests ordered by latest

    return render(request, 'guest_info.html', {'guests_by_month': guests_by_month, 'guests': guests})


def guest_detail(request, pk):
    guest = get_object_or_404(Guest, pk=pk)
    satisfaction = guest.satisfaction_responses.all()
    purposes = guest.stay_purposes.all()
    comments = guest.comments.all()

    context = {
        'guest': guest,
        'satisfaction': satisfaction,
        'purposes': purposes,
        'comments': comments,
    }
    return render(request, 'guest_detail.html', context)


# Login View
def custom_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('guest_info')  # Redirect to guest info page after login
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'login.html')

# Logout View
def custom_logout(request):
    logout(request)
    return redirect('custom_login')  # Redirect back to login page



from datetime import datetime
from collections import defaultdict
from django.shortcuts import render
from django.db.models import Count
from .models import Guest, SatisfactionResponse

def satisfaction_analysis(request):
    # Get month and year
    today = datetime.today()
    current_month = int(request.GET.get('month', today.month))
    current_year = int(request.GET.get('year', today.year))

    # Filter guests and responses
    guests = Guest.objects.filter(date_submitted__month=current_month, date_submitted__year=current_year)
    responses = SatisfactionResponse.objects.filter(guest__in=guests)

    # Analyze
    analysis = {}
    for question in responses.values_list('question__text', flat=True).distinct():
        q_responses = responses.filter(question__text=question)
        total_count = q_responses.count()
        counts = q_responses.values('rating').annotate(total=Count('rating'))

        happy = neutral = sad = 0
        for item in counts:
            if item['rating'] == 'happy':
                happy = item['total']
            elif item['rating'] == 'neutral':
                neutral = item['total']
            elif item['rating'] == 'sad':
                sad = item['total']

        if total_count > 0:
            analysis[question] = {
                'happy': (happy / total_count) * 100,
                'neutral': (neutral / total_count) * 100,
                'sad': (sad / total_count) * 100
            }

    context = {
        'month': datetime(current_year, current_month, 1).strftime('%B %Y'),
        'analysis': analysis,
        'month_options': list(range(1, 13)),
        'year_options': list(range(2023, today.year + 2)),
        'current_month': current_month,
        'current_year': current_year,
    }
    return render(request, 'satisfaction_analysis.html', context)



from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from openpyxl import Workbook

def download_pdf(request):
    # Use the same logic from satisfaction_analysis view
    # Reuse logic to get context:
    from .views import get_analysis_context  # helper you'll define below
    context = get_analysis_context(request)

    template_path = 'satisfaction_pdf_template.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="satisfaction_analysis.pdf"'
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors with PDF generation <pre>' + html + '</pre>')
    return response


def download_excel(request):
    from .views import get_analysis_context
    context = get_analysis_context(request)
    analysis = context['analysis']

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Satisfaction Analysis"

    # Header
    sheet.append(['Category', '😀 Happy (%)', '😐 Neutral (%)', '😞 Sad (%)'])

    for question, ratings in analysis.items():
        sheet.append([
            question,
            round(ratings['happy']),
            round(ratings['neutral']),
            round(ratings['sad']),
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="satisfaction_analysis.xlsx"'
    workbook.save(response)
    return response


def get_analysis_context(request):
    from datetime import datetime
    month = request.GET.get('month')
    year = request.GET.get('year')
    today = datetime.today()
    month = int(month) if month else today.month
    year = int(year) if year else today.year

    guests = Guest.objects.filter(date_submitted__month=month, date_submitted__year=year)
    responses = SatisfactionResponse.objects.filter(guest__in=guests)

    analysis = {}
    for question in responses.values_list('question__text', flat=True).distinct():
        q_responses = responses.filter(question__text=question)
        counts = q_responses.values('rating').annotate(total=Count('rating'))
        total = q_responses.count()
        analysis[question] = {
            'happy': 0,
            'neutral': 0,
            'sad': 0
        }
        for item in counts:
            percent = (item['total'] / total) * 100 if total > 0 else 0
            analysis[question][item['rating']] = percent

    return {
        'month': datetime(year, month, 1).strftime('%B %Y'),
        'analysis': analysis,
        'current_month': month,
        'current_year': year,
        'month_options': list(range(1, 13)),
        'year_options': list(range(2023, today.year + 1))
    }
