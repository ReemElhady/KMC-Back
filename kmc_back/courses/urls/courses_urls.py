from django.urls import path

from courses.views.courses_view import (
    BranchSListView,
    CourseSListView,
    SingleCourseView,
    BrandListView,
)


urlpatterns = [
    # path("<int:type_id>", CourseSListView.as_view(), name="coursesList"),
    path("", CourseSListView.as_view(), name="coursesList"),
    path("details/<int:pk>", SingleCourseView.as_view(), name="singleCurse"),
    path("branch/<int:type_id>", BranchSListView.as_view(), name="coursesBranches"),
    path("brand", BrandListView.as_view(), name="brands_list"),
]
