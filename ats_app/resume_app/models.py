from django.db import models

class Candidate(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    linkedin = models.CharField(max_length=500, null=True, blank=True)
    college = models.CharField(max_length=255, null=True, blank=True)
    cgpa = models.CharField(max_length=10, null=True, blank=True)
    experience = models.CharField(max_length=50, null=True, blank=True)

    role = models.CharField(max_length=100)
    score = models.FloatField()

    matched_skills = models.TextField()
    missing_skills = models.TextField()

    uploaded_at = models.DateTimeField(auto_now_add=True)

    resume_file = models.FileField(upload_to="resumes/", null=True, blank=True)


    def __str__(self):
        return self.name or "Candidate"
