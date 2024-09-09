from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class PointsAPIView(ListAPIView):
    # serializer_class = PointsSerializer
    permission_classes = [IsAuthenticated]

    # def get_queryset(self):
    # return Points.objects.filter(expire_date__gte=datetime.today().date(), is_expired=False,
    #                              user=self.request.user,points__gt=0).select_related('order').order_by('expire_date')

    def list(self, request, *args, **kwargs):
        # set_points_expired_as_boolean(request.user)
        # query = self.get_queryset()
        # today = datetime.today().date()
        #
        # total_points_query = self.get_queryset().filter(expire_date__gte=today, is_expired=False).aggregate(
        #     total_points=Sum('points'), total_used_points=Sum('used_points'))
        # if total_points_query.get('total_points') is None:
        #     total_points = 0
        # else:
        #     total_points = total_points_query.get('total_points', 0)
        #
        # one_point_value = General.objects.first().point_value
        # total_points_value = total_points * one_point_value
        #
        # if total_points_query.get('total_used_points') is None:
        #     total_used_points = 0
        # else:
        #     total_used_points = total_points_query.get('total_used_points', 0)
        #
        # serializer = PointsSerializer(query, many=True).data
        # first_points_to_expire = None
        # first_points_to_expire_date = None
        # if query.first():
        #     first_points_to_expire_query = query.filter(points__gt=0).first()
        #     if first_points_to_expire_query:
        #         first_points_to_expire = first_points_to_expire_query.points
        #         first_points_to_expire_date = first_points_to_expire_query.expire_date
        # return Response(
        #     {
        #         'points_list': serializer,
        #         'total_points': total_points,
        #         'total_points_value': total_points_value,
        #         'first_points_to_expire': first_points_to_expire,
        #         'first_points_to_expire_date': first_points_to_expire_date,
        #         'total_used_points': total_used_points
        #     }, status=status.HTTP_200_OK)
        return Response(
            {
                'points_list': [],
                'total_points': 0,
                'total_points_value': 0,
                'first_points_to_expire': 0,
                'first_points_to_expire_date': 0,
                'total_used_points': 0
            }, status=status.HTTP_200_OK)
