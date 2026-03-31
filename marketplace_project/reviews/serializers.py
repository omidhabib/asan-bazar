from rest_framework import serializers
from .models import Review
from django.db.models import Avg

class ReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.ReadOnlyField(source='reviewer.full_name')
    target_user_name = serializers.ReadOnlyField(source='target_user.full_name')

    class Meta:
        model = Review
        fields = ['id', 'reviewer', 'reviewer_name', 'target_user', 'target_user_name', 'ad', 'rating', 'comment', 'created_at']
        read_only_fields = ['reviewer', 'target_user', 'created_at']

    def validate(self, data):
        ad = data.get('ad')
        if ad:
            data['target_user'] = ad.user
        return data

class UserRatingStatsSerializer(serializers.Serializer):
    target_user_id = serializers.IntegerField()
    average_rating = serializers.FloatField()
    total_reviews = serializers.IntegerField()
