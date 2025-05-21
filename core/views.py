from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.db import connection
from django.utils import timezone
from django.contrib import messages
from .models import REAPCycle, REAPQuestion, REAPUserAnswer, REAPUserMapping
from datetime import datetime, timedelta
from django.db.models import Q
from django.http import Http404

# Create your views here.

class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if not self.request.user.is_authenticated:
            return context
            
        now = timezone.now()
        
        # Get all evaluations for the user
        user_mappings = REAPUserMapping.objects.filter(user=self.request.user)
        
        # Get active evaluations (where end_date is in the future)
        active_evaluations = REAPCycle.objects.filter(
            Q(end_date__gte=now) &
            Q(reapusermapping__user=self.request.user)
        ).distinct()
        
        # Get completed evaluations (where user has submitted their evaluation)
        completed_evaluations = user_mappings.filter(
            status='EMPLOYEE_SUBMITTED'
        ).values_list('reap', flat=True).distinct()
        
        # Get total evaluations (all mappings for the user)
        total_evaluations = user_mappings.values_list('reap', flat=True).distinct()
        
        # Add submission status to active cycles
        for cycle in active_evaluations:
            cycle.is_submitted = REAPUserAnswer.objects.filter(
                reap=cycle,
                user=self.request.user,
                submitted_user=self.request.user,
                is_submit=True
            ).exists()
        
        context.update({
            'active_evaluations': active_evaluations,
            'active_evaluations_count': active_evaluations.count(),
            'completed_evaluations_count': completed_evaluations.count(),
            'total_evaluations_count': total_evaluations.count(),
        })
        
        return context

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        return super().get(request, *args, **kwargs)

@login_required
def evaluation_list(request):
    # Get all REAP cycles
    cycles = REAPCycle.objects.all().order_by('-end_date')
    now = timezone.now()
    
    # Check if user is a reporting manager
    is_rm = REAPUserMapping.objects.filter(rm=request.user).exists()
    
    # Check if user is a CTM
    is_ctm = REAPUserMapping.objects.filter(ctm=request.user).exists()
    
    # Get reportee mappings if user is RM
    reportee_mappings = []
    if is_rm:
        reportee_mappings = REAPUserMapping.objects.filter(
            rm=request.user
        ).select_related('user', 'reap').order_by('-reap__end_date')
        
        # Add status flags for each mapping
        for mapping in reportee_mappings:
            mapping.is_submitted = REAPUserAnswer.objects.filter(
                reap=mapping.reap,
                user=mapping.user,
                is_submit=True
            ).exists()
            
            mapping.has_answers = REAPUserAnswer.objects.filter(
                reap=mapping.reap,
                user=mapping.user
            ).exists()
    
    # Get dotted reportee mappings if user is CTM
    dotted_reportee_mappings = []
    if is_ctm:
        dotted_reportee_mappings = REAPUserMapping.objects.filter(
            ctm=request.user
        ).select_related('user', 'reap').order_by('-reap__end_date')
        
        # Add status flags for each mapping
        for mapping in dotted_reportee_mappings:
            mapping.is_submitted = REAPUserAnswer.objects.filter(
                reap=mapping.reap,
                user=mapping.user,
                submitted_user=request.user,
                is_submit=True
            ).exists()
            
            mapping.has_answers = REAPUserAnswer.objects.filter(
                reap=mapping.reap,
                user=mapping.user,
                submitted_user=request.user
            ).exists()
            
            # Add submission status for employee and RM
            mapping.user_submitted_at = REAPUserAnswer.objects.filter(
                reap=mapping.reap,
                user=mapping.user,
                submitted_user=mapping.user,
                is_submit=True
            ).exists()
            
            mapping.rm_submitted_at = REAPUserAnswer.objects.filter(
                reap=mapping.reap,
                user=mapping.user,
                submitted_user=mapping.rm,
                is_submit=True
            ).exists()
            
            # Use status field for CTM status
            mapping.pgm_submitted_at = mapping.status == 'PGM_SUBMITTED'
    
    # Add status flags for each cycle
    for cycle in cycles:
        cycle.is_submitted = REAPUserAnswer.objects.filter(
            reap=cycle,
            user=request.user,
            is_submit=True
        ).exists()
        
        cycle.has_answers = REAPUserAnswer.objects.filter(
            reap=cycle,
            user=request.user
        ).exists()
    
    # Split cycles into active and inactive
    active_cycles = [cycle for cycle in cycles if cycle.end_date > now]
    inactive_cycles = [cycle for cycle in cycles if cycle.end_date <= now]
    
    context = {
        'active_cycles': active_cycles,
        'inactive_cycles': inactive_cycles,
        'is_rm': is_rm,
        'reportee_mappings': reportee_mappings,
        'is_ctm': is_ctm,
        'dotted_reportee_mappings': dotted_reportee_mappings,
    }
    
    return render(request, 'core/evaluation_list.html', context)

@login_required
def evaluation_form(request, reap_id, user_id=None, dotted_manager_id=None):
    # Get the specific REAP cycle
    current_cycle = get_object_or_404(REAPCycle, id=reap_id)
    
    # If only reap_id is provided, show a simple view
    if user_id is None:
        # Get questions for this cycle
        questions = REAPQuestion.objects.filter(
            reap=current_cycle
        ).order_by('sequence')

        # Get user's answers
        user_answers = REAPUserAnswer.objects.filter(
            reap=current_cycle,
            user=request.user,
            submitted_user=request.user
        ).values('reap_question_id', 'answer_text', 'is_submit')

        # Convert to dictionary for template
        answers_dict = {ans['reap_question_id']: ans['answer_text'] for ans in user_answers}
        is_submitted = any(ans['is_submit'] for ans in user_answers)

        # Calculate time remaining
        now = timezone.now()
        time_remaining = current_cycle.end_date - now
        days_remaining = time_remaining.days
        hours_remaining = time_remaining.seconds // 3600

        # Check if the cycle has expired
        is_expired = current_cycle.end_date < now

        context = {
            'current_cycle': current_cycle,
            'questions': questions,
            'user_answers': answers_dict,
            'is_submitted': is_submitted,
            'now': now,
            'days_remaining': days_remaining,
            'hours_remaining': hours_remaining,
            'end_date_display': current_cycle.end_date.strftime('%B %d, %Y %I:%M %p'),
            'is_expired': is_expired,
            'target_user': request.user,
            'is_simple_view': True
        }
        return render(request, 'core/evaluation_form.html', context)
    
    # Determine if this is a RM evaluation, PGM evaluation, or CTM evaluation
    is_rm_evaluation = False
    is_pgm_evaluation = False
    is_ctm_evaluation = False
    target_user = request.user
    
    if user_id is not None:
        # Check if user is RM for the target user
        rm_mapping = REAPUserMapping.objects.filter(
            reap=current_cycle,
            user_id=user_id,
            rm=request.user
        ).first()
        
        # Check if user is PGM for the target user
        pgm_mapping = REAPUserMapping.objects.filter(
            reap=current_cycle,
            user_id=user_id,
            pgm=request.user
        ).first()
        
        # Check if user is CTM for the target user
        ctm_mapping = REAPUserMapping.objects.filter(
            reap=current_cycle,
            user_id=user_id,
            ctm=request.user
        ).first()
        
        if rm_mapping:
            is_rm_evaluation = True
            target_user = rm_mapping.user
        elif pgm_mapping:
            is_pgm_evaluation = True
            target_user = pgm_mapping.user
            # Get the RM mapping for this user
            rm_mapping = REAPUserMapping.objects.filter(
                reap=current_cycle,
                user=target_user
            ).first()
        elif ctm_mapping:
            is_ctm_evaluation = True
            target_user = ctm_mapping.user
            # Get the RM mapping for this user
            rm_mapping = REAPUserMapping.objects.filter(
                reap=current_cycle,
                user=target_user
            ).first()
        else:
            raise Http404("You are not authorized to evaluate this user.")
    
    # Check if user is a reporting manager and get their reportees
    has_reportees = REAPUserMapping.objects.filter(rm=request.user).exists()
    reportee_mappings = []
    if has_reportees:
        reportee_mappings = REAPUserMapping.objects.filter(
            rm=request.user,
            reap=current_cycle
        ).select_related('user', 'reap')
        
        # Add submission status for each mapping
        for mapping in reportee_mappings:
            mapping.is_submitted = REAPUserAnswer.objects.filter(
                reap=mapping.reap,
                user=mapping.user,
                is_submit=True
            ).exists()
    
    # Check if user is a CTM and get their dotted reportees
    is_ctm = REAPUserMapping.objects.filter(ctm=request.user).exists()
    dotted_reportee_mappings = []
    if is_ctm:
        dotted_reportee_mappings = REAPUserMapping.objects.filter(
            ctm=request.user,
            reap=current_cycle
        ).select_related('user', 'reap')
        
        # Add submission status for each mapping
        for mapping in dotted_reportee_mappings:
            mapping.is_submitted = REAPUserAnswer.objects.filter(
                reap=mapping.reap,
                user=mapping.user,
                submitted_user=request.user,
                is_submit=True
            ).exists()
    
    questions = REAPQuestion.objects.filter(
        reap=current_cycle
    ).order_by('sequence')

    # Fetch previous answers
    user_answers = REAPUserAnswer.objects.filter(
        reap=current_cycle,
        user=target_user,
        submitted_user=request.user if (is_rm_evaluation or is_ctm_evaluation) else target_user
    ).values('reap_question_id', 'answer_text', 'is_submit')

    # Convert to dictionary for template
    answers_dict = {ans['reap_question_id']: ans['answer_text'] for ans in user_answers}
    
    # Check if the evaluation is submitted
    if is_ctm_evaluation:
        is_submitted = mapping.status == 'PGM_SUBMITTED'
    elif is_rm_evaluation:
        is_submitted = mapping.status == 'RM_SUBMITTED'
    else:
        is_submitted = mapping.status == 'EMPLOYEE_SUBMITTED'

    # Get employee's answers
    employee_answers = REAPUserAnswer.objects.filter(
        reap=current_cycle,
        user=target_user,
        submitted_user=target_user
    ).values('reap_question_id', 'answer_text')
    employee_answers = {ans['reap_question_id']: ans['answer_text'] for ans in employee_answers}

    # Get RM's answers if this is a CTM evaluation
    rm_answers = {}
    if is_ctm_evaluation and rm_mapping:
        rm_answers = REAPUserAnswer.objects.filter(
            reap=current_cycle,
            user=target_user,
            submitted_user=rm_mapping.rm
        ).values('reap_question_id', 'answer_text')
        rm_answers = {ans['reap_question_id']: ans['answer_text'] for ans in rm_answers}

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'clear' and not is_submitted and current_cycle.end_date >= timezone.now():
            # Clear all answers for this cycle and user
            REAPUserAnswer.objects.filter(
                reap=current_cycle,
                user=target_user,
                submitted_user=request.user if (is_rm_evaluation or is_ctm_evaluation) else target_user
            ).delete()
            messages.success(request, "Form has been cleared.")
            return redirect('core:evaluation_form', reap_id=reap_id, user_id=user_id, dotted_manager_id=dotted_manager_id)
        
        elif action in ['save', 'submit']:
            # Get the mapping for this evaluation
            if is_rm_evaluation:
                mapping = get_object_or_404(REAPUserMapping, reap=current_cycle, user=target_user, rm=request.user)
            elif is_pgm_evaluation:
                mapping = get_object_or_404(REAPUserMapping, reap=current_cycle, user=target_user, pgm=request.user)
            elif is_ctm_evaluation:
                print(f"Looking for CTM mapping - reap: {current_cycle.id}, user: {target_user.id}, ctm: {request.user.id}")
                # For CTM evaluation, we need to get the mapping where the user is the CTM
                mapping = get_object_or_404(REAPUserMapping, reap=current_cycle, user=target_user, ctm=request.user)
                print(f"Found mapping - ID: {mapping.id}, Status: {mapping.status}")
            else:
                mapping = get_object_or_404(REAPUserMapping, reap=current_cycle, user=target_user)
            
            # Check if the evaluation can be submitted
            if action == 'submit':
                if is_rm_evaluation and not mapping.user_submitted_at:
                    messages.error(request, "Employee must submit their evaluation first.")
                    return redirect('core:evaluation_form', reap_id=reap_id, user_id=user_id, dotted_manager_id=dotted_manager_id)
                elif (is_pgm_evaluation or is_ctm_evaluation) and not mapping.rm_submitted_at:
                    messages.error(request, "Reporting Manager must submit their evaluation first.")
                    return redirect('core:evaluation_form', reap_id=reap_id, user_id=user_id, dotted_manager_id=dotted_manager_id)
            
            # Process each question
            for question in questions:
                answer_text = request.POST.get(f'answer_{question.id}')
                if answer_text:
                    REAPUserAnswer.objects.update_or_create(
                        reap=current_cycle,
                        user=target_user,
                        reap_question=question,
                        submitted_user=request.user if (is_rm_evaluation or is_ctm_evaluation) else target_user,
                        defaults={
                            'answer_text': answer_text,
                            'is_submit': action == 'submit'
                        }
                    )
            
            if action == 'submit':
                # Update the mapping status
                if is_rm_evaluation:
                    mapping.status = 'RM_SUBMITTED'
                    mapping.rm_submitted_at = timezone.now()
                elif is_pgm_evaluation or is_ctm_evaluation:
                    print(f"Updating status for {'PGM' if is_pgm_evaluation else 'CTM'} evaluation")
                    print(f"Current status: {mapping.status}")
                    # For CTM evaluation, we treat it as PGM submission
                    mapping.status = 'PGM_SUBMITTED'
                    mapping.pgm_submitted_at = timezone.now()
                    print(f"New status: {mapping.status}")
                else:
                    mapping.status = 'EMPLOYEE_SUBMITTED'
                    mapping.user_submitted_at = timezone.now()
                
                try:
                    mapping.save()
                    print(f"Status saved successfully: {mapping.status}")
                    messages.success(request, "Form submitted successfully!")
                except Exception as e:
                    print(f"Error saving status: {str(e)}")
                    messages.error(request, f"Error saving status: {str(e)}")
                    return redirect('core:evaluation_form', reap_id=reap_id, user_id=user_id, dotted_manager_id=dotted_manager_id)
            else:
                messages.success(request, "Form saved successfully!")
            
            return redirect('core:evaluation_form', reap_id=reap_id, user_id=user_id, dotted_manager_id=dotted_manager_id)

    # Calculate time remaining
    now = timezone.now()
    time_remaining = current_cycle.end_date - now
    days_remaining = time_remaining.days
    hours_remaining = time_remaining.seconds // 3600

    # Check if the cycle has expired
    is_expired = current_cycle.end_date < now

    context = {
        'current_cycle': current_cycle,
        'questions': questions,
        'user_answers': answers_dict,
        'employee_answers': employee_answers,
        'rm_answers': rm_answers,
        'is_submitted': is_submitted,
        'now': now,
        'days_remaining': days_remaining,
        'hours_remaining': hours_remaining,
        'end_date_display': current_cycle.end_date.strftime('%B %d, %Y %I:%M %p'),
        'is_expired': is_expired,
        'is_rm_evaluation': is_rm_evaluation,
        'is_ctm_evaluation': is_ctm_evaluation,
        'target_user': target_user,
        'has_reportees': has_reportees,
        'reportee_mappings': reportee_mappings,
        'is_ctm': is_ctm,
        'dotted_reportee_mappings': dotted_reportee_mappings,
        'dotted_manager_id': dotted_manager_id,
        'rm_mapping': rm_mapping if is_ctm_evaluation else None
    }
    
    return render(request, 'core/evaluation_form.html', context)
