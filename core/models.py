from django.db import models
from users.models import User
from django.utils import timezone

# Create your models here.

class REAPCycle(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
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
        ('objective', 'Objective'),
        ('rating', 'Rating'),
    )

    VISIBLE_TO_CHOICES = (
        ('EMPLOYEE', 'Employee'),
        ('RM', 'RM'),
        ('PGM', 'PGM'),
        ('ALL', 'All'),
    )
    
    reap = models.ForeignKey(REAPCycle, on_delete=models.CASCADE, db_column='reap_id')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    sequence = models.IntegerField()
    is_mandatory = models.BooleanField(default=True)
    visible_to = models.CharField(max_length=50, choices=VISIBLE_TO_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sequence}. {self.question_text}"

    class Meta:
        db_table = 'reap_questions'
        ordering = ['sequence']

class REAPUserAnswer(models.Model):
    reap = models.ForeignKey(REAPCycle, on_delete=models.CASCADE, db_column='reap_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_answers')
    submitted_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_answers')
    reap_question = models.ForeignKey(REAPQuestion, on_delete=models.CASCADE, db_column='reap_question_id')
    answer_text = models.TextField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    is_auto_submitted = models.BooleanField(default=False)
    submitted_on = models.DateTimeField(auto_now_add=True)
    is_submit = models.BooleanField(default=False)

    class Meta:
        db_table = 'reap_user_answers'

    def __str__(self):
        return f"{self.user.username} - {self.reap_question.question_text}"
