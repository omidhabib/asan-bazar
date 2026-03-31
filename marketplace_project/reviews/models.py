from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

class Review(models.Model):
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_given')
    target_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_received')
    ad = models.ForeignKey('ads.Ad', on_delete=models.CASCADE, related_name='reviews', null=True)
    
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('reviewer', 'ad')
        ordering = ['-created_at']

    def clean(self):
        if self.reviewer == self.target_user:
            raise ValidationError("You cannot rate or review your own ad.")
        if self.ad and self.ad.user != self.target_user:
             # Auto-correct target_user to the ad owner
             self.target_user = self.ad.user

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reviewer} -> {self.target_user} ({self.rating} stars)"
