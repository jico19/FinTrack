from django.db import models
from django.contrib.auth.models import User

class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='badges/', null=True, blank=True)
    icon_code = models.CharField(max_length=50, null=True, blank=True, help_text="Tailwind/Lucide icon name")

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    budget = models.PositiveIntegerField(default=0)
    total_points = models.PositiveIntegerField(default=0)
    current_streak = models.PositiveIntegerField(default=0)
    best_streak = models.PositiveIntegerField(default=0)
    last_logged_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"User Profile -> #{self.user.pk}"

class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="badges")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')

    def __str__(self):
        return f"{self.user.username} earned {self.badge.name}"

class Challenge(models.Model):
    """
    F-15: Weekly challenges that users can complete for bonus points.
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    points_reward = models.PositiveIntegerField(default=50)
    target_count = models.PositiveIntegerField(default=5, help_text="Number of records needed to complete")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class UserChallengeProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="challenge_progress")
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    current_count = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'challenge')

    def __str__(self):
        return f"{self.user.username} - {self.challenge.title} ({self.current_count}/{self.challenge.target_count})"
