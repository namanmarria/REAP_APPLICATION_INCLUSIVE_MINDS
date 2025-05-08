from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.db import connection
from django.utils import timezone
from django.contrib import messages
from .models import REAPCycle, REAPQuestion, REAPUserAnswer
from datetime import datetime, timedelta

# Create your views here.

class HomeView(TemplateView):
    template_name = 'core/home.html'

@login_required
def evaluation_list(request):
    reap_cycles = REAPCycle.objects.all().order_by('-end_date')
    
    # Check if each cycle has been submitted by the current user
    for cycle in reap_cycles:
        cycle.is_submitted = REAPUserAnswer.objects.filter(
            user=request.user,
            reap=cycle,
            is_submit=True
        ).exists()
    
    context = {
        'reap_cycles': reap_cycles,
        'now': timezone.now()
    }
    return render(request, 'core/evaluation_list.html', context)

@login_required
def evaluation_form(request, reap_id):
    # Get the specific REAP cycle
    current_cycle = get_object_or_404(REAPCycle, id=reap_id)
    
    user = request.user
    questions = REAPQuestion.objects.filter(
        reap=current_cycle
    ).order_by('sequence')

    # Fetch previous answers
    user_answers = REAPUserAnswer.objects.filter(
        reap=current_cycle,
        user=user
    ).values('reap_question_id', 'answer_text', 'is_submit')

    # Convert to dictionary for template
    answers_dict = {ans['reap_question_id']: ans['answer_text'] for ans in user_answers}
    is_submitted = any(ans['is_submit'] for ans in user_answers)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'clear' and not is_submitted and current_cycle.end_date >= timezone.now():
            # Clear all answers for this cycle and user
            REAPUserAnswer.objects.filter(
                reap=current_cycle,
                user=user
            ).delete()
            messages.success(request, "Form has been cleared.")
            return redirect('core:evaluation_form', reap_id=reap_id)

        if action in ['save', 'submit'] and not is_submitted and current_cycle.end_date >= timezone.now():
            # Validate form
            errors = []
            for question in questions:
                if question.is_mandatory:
                    answer = request.POST.get(f'answer_{question.id}', '').strip()
                    if not answer:
                        errors.append(f"Question {question.sequence} is mandatory.")

            if errors:
                for error in errors:
                    messages.error(request, error)
                return redirect('core:evaluation_form', reap_id=reap_id)

            # Process answers
            for question in questions:
                answer_text = request.POST.get(f'answer_{question.id}', '').strip()
                if answer_text:
                    REAPUserAnswer.objects.update_or_create(
                        reap=current_cycle,
                        user=user,
                        submitted_user=user,
                        reap_question=question,
                        defaults={
                            'answer_text': answer_text,
                            'is_submit': action == 'submit'
                        }
                    )

            if action == 'submit':
                messages.success(request, "Form submitted successfully!")
            else:
                messages.success(request, "Form saved successfully!")
            
            return redirect('core:evaluation_form', reap_id=reap_id)

    # Calculate time remaining
    now = timezone.now()
    time_remaining = current_cycle.end_date - now
    days_remaining = time_remaining.days
    hours_remaining = time_remaining.seconds // 3600

    context = {
        'cycle': current_cycle,
        'questions': questions,
        'user_answers': answers_dict,
        'is_submitted': is_submitted,
        'now': now,
        'days_remaining': days_remaining,
        'hours_remaining': hours_remaining,
        'end_date_display': current_cycle.end_date.strftime('%B %d, %Y %I:%M %p')
    }
    
    return render(request, 'core/evaluation_form.html', context)
