from rest_framework import serializers

from points.models.points_models import Points


# class PointsSerializer(serializers.ModelSerializer):
#     order_id = serializers.CharField(source='order.code')
#     created_at = serializers.SerializerMethodField()
#
#     def get_created_at(self, obj):
#         return obj.order.created_at.strftime("%Y-%m-%d")
#
#     class Meta:
#         model = Points
#         fields = ('order_id', 'created_at', 'points', 'is_expired', 'used_points',)
