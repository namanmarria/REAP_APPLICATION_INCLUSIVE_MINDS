from django.shortcuts import render, redirect
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
def evaluation_form(request):
    # Get the active REAP cycle
    try:
        current_cycle = REAPCycle.objects.filter(
            end_date__gt=timezone.now()
        ).latest('end_date')
    except REAPCycle.DoesNotExist:
        messages.error(request, "No active REAP cycle found.")
        return redirect('core:home')

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
        
        if action == 'clear' and not is_submitted:
            # Clear all answers for this cycle and user
            REAPUserAnswer.objects.filter(
                reap=current_cycle,
                user=user
            ).delete()
            messages.success(request, "Form has been cleared.")
            return redirect('core:evaluation_form')

        if action in ['save', 'submit'] and not is_submitted:
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
                return redirect('core:evaluation_form')

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
            
            return redirect('core:evaluation_form')

    context = {
        'cycle': current_cycle,
        'questions': questions,
        'user_answers': answers_dict,
        'is_submitted': is_submitted,
    }
    
    return render(request, 'core/evaluation_form.html', context)
