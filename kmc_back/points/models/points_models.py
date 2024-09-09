# from django.contrib.auth import get_user_model
# from django.db import models
#
# from order.models.order_models import Order
#
#
# class Points(models.Model):
#     points = models.PositiveIntegerField(default=0)
#     user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='points_user')
#     expire_date = models.DateField()
#     is_expired = models.BooleanField(default=False)
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='point_order')
#     used_points = models.PositiveIntegerField(default=0)
#
#     class Meta:
#         verbose_name_plural = 'Points'
