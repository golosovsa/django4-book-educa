from django.urls import path
from . import views

urlpatterns = [
    path('mine/', views.ManageCourseListView.as_view(), name='manage_course_list'),
    path('create/', views.CourseCreateView.as_view(), name='course_create'),
    path('<pk>/edit/', views.CourseUpdateView.as_view(), name='course_edit'),
    path('<pk>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),
    path('<pk>/module/', views.CourseModuleUpdateView.as_view(), name='course_module_update'),
    path('module/<int:module_pk>/content/<model_name>/create/',
         views.ContentCreateUpdateView.as_view(),
         name='module_content_create'),
    path('module/<int:module_pk>/content/<model_name>/<pk>/',
         views.ContentCreateUpdateView.as_view(),
         name='module_content_update'),
    path('module/order/', views.ModuleOrderView.as_view(), name='module_order'),
    path('module/<int:module_pk>/', views.ModuleContentListView.as_view(), name='module_content_list'),
    path('content/<int:pk>/delete/', views.CourseDeleteView.as_view(), name='module_content_delete'),
    path('content/order/', views.ContentOrderView.as_view(), name='content_order'),
]
