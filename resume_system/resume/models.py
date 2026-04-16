from django.conf import settings
from django.db import models

class Resume(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resumes',
        null=True,
        blank=True,
    )
    file = models.FileField(upload_to='resume/')
    job_description = models.TextField(default='', help_text="Enter the job description")
    
    # Final Match Score (Manual NLP Match)
    score = models.IntegerField(null=True, blank=True)
    
    # Keep grammar if you want the report, but DELETE the others
    grammar_score = models.IntegerField(null=True, blank=True)
    
    # REMOVED: tone_score and ai_likelihood_score (This stops the KeyError)
    
    # Storage for NLP Results
    matched_skills = models.TextField(null=True, blank=True)
    missing_skills = models.TextField(null=True, blank=True)
    
    # Suggestions for the user
    ai_suggestions = models.TextField(null=True, blank=True) 
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_part = self.user.username if self.user else 'anonymous'
        return f"{user_part} - {self.file.name}"