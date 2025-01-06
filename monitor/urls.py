from django.urls import path, include
from . import views

from rest_framework.routers import DefaultRouter
from .views import CalendarTaskViewSet, TodoTaskViewSet

router = DefaultRouter()
router.register('calendar-tasks', CalendarTaskViewSet)
router.register('todo-tasks', TodoTaskViewSet)

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),
    path('input/', views.input_view, name='input'),
    path('chart/', views.chart_view, name='chart'),
    path('download_excel/', views.export_to_excel_view, name='download_excel'),  # URL mapping for downloading Excel
    path('calendar/', views.calendar_view, name='calendar'),
    path('delete-quote/<int:id>/', views.delete_quote, name='delete_quote'),
    
    # To make frontend interact with the SQLite through these API endpoints
    path('api/', include(router.urls)),
    path('api/load-tasks/', views.load_tasks, name='load-tasks'),

]


