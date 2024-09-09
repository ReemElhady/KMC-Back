# from datetime import datetime
#
# from django.db import transaction
# from django.db.models import F, Sum
# from rest_framework.exceptions import NotAcceptable
#
# from general.models.general_model import General
# from points.models.points_models import Points
#
#
# def set_points_expired_as_boolean(user):
#     today = datetime.today().date()
#     Points.objects.filter(user=user, is_expired=False, expire_date__lte=today).update(is_expired=True)
#
#
# def use_points(points, user):
#     with transaction.atomic():
#         if get_total_points(user) < points:
#             raise NotAcceptable('No enough points found')
#         if points % 1000 == 0 and General.objects.exists():
#             orders_points = Points.objects.filter(expire_date__gte=datetime.today().date(), is_expired=False, user=user,
#                                                   points__gt=0).order_by(
#                 'expire_date')
#             used_points = points
#             for order_points in orders_points:
#
#                 if order_points.points >= used_points:
#                     order_points.points -= used_points
#                     order_points.used_points += used_points
#                     break
#                 else:
#                     used_points -= order_points.points
#                     order_points.used_points += order_points.points
#                     order_points.points = 0
#
#             Points.objects.bulk_update(orders_points, ['points', 'used_points'])
#             return General.objects.first().point_value * points
#         return 'Inapplicable'
#
#
# def get_total_points(user):
#     total_points = Points.objects.filter(expire_date__gte=datetime.today().date(), is_expired=False,
#                                          user=user,points__gt=0).aggregate(
#         total_points=Sum('points'))
#     if total_points['total_points'] is None:
#         return 0
#     else:
#         return total_points['total_points']
