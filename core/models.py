from django.db import models
from users.models import User
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.

class REAPCycle(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Ensure datetime fields are timezone-aware
        if timezone.is_naive(self.start_date):
            self.start_date = timezone.make_aware(self.start_date)
        if timezone.is_naive(self.end_date):
            self.end_date = timezone.make_aware(self.end_date)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'reap_cycles'
        ordering = ['-end_date']

class REAPQuestion(models.Model):
    QUESTION_TYPES = (
        ('subjective', 'Subjective'),
        ('rating', 'Rating'),
    )

    VISIBLE_TO_CHOICES = (
        ('EMPLOYEE', 'Employee'),
        ('RM', 'RM'),
        ('PGM', 'PGM'),
        ('ALL', 'All'),
    )
    
    reap = models.ForeignKey(REAPCycle, on_delete=models.CASCADE, null=True)
    sequence = models.IntegerField()
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    is_mandatory = models.BooleanField(default=False)
    visible_to = models.CharField(max_length=50, choices=VISIBLE_TO_CHOICES, default='ALL')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sequence}. {self.question_text}"

    class Meta:
        db_table = 'reap_questions'
        ordering = ['sequence']

class REAPUserMapping(models.Model):
    STATUS_CHOICES = (
        ('EMPLOYEE_PENDING', 'Employee Pending'),
        ('EMPLOYEE_SUBMITTED', 'Employee Submitted'),
        ('RM_PENDING', 'RM Pending'),
        ('RM_SUBMITTED', 'RM Submitted'),
        ('CTM_PENDING', 'CTM Pending'),
        ('CTM_SUBMITTED', 'CTM Submitted'),
        ('PGM_PENDING', 'PGM Pending'),
        ('PGM_COMPLETED', 'PGM Completed'),
    )

    reap = models.ForeignKey(REAPCycle, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_mappings')
    rm = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rm_mappings')
    pgm = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pgm_mappings')
    ctm = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ctm_mappings')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='EMPLOYEE_PENDING')
    user_submitted_at = models.DateTimeField(null=True, blank=True)
    rm_submitted_at = models.DateTimeField(null=True, blank=True)
    pgm_submitted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reap_user_mappings'
        unique_together = ('reap', 'user')

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.reap.name}"

class REAPUserAnswer(models.Model):
    reap = models.ForeignKey(REAPCycle, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reap_answers')
    submitted_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_answers', null=True)
    reap_question = models.ForeignKey(REAPQuestion, on_delete=models.CASCADE)
    answer_text = models.TextField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    is_auto_submitted = models.BooleanField(default=False)
    submitted_on = models.DateTimeField(auto_now_add=True)
    is_submit = models.BooleanField(default=False)

    class Meta:
        db_table = 'reap_user_answers'
        unique_together = ('reap', 'user', 'submitted_user', 'reap_question')
        ordering = ['reap_question__sequence']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.reap_question.question_text[:50]}"
