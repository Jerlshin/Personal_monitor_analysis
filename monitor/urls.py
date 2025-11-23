from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import CalendarTaskViewSet, TodoTaskViewSet

router = DefaultRouter()
router.register('calendar-tasks', CalendarTaskViewSet)
router.register('todo-tasks', TodoTaskViewSet)

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login_direct'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),
    
    # New Settings Page
    path('settings/', views.settings_view, name='settings'),
    
    path('input/', views.input_view, name='input'),
    path('chart/', views.chart_view, name='chart'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('plan-ideas/', views.plan_ideas, name='plan_ideas'),
    
    # Changed from download_excel to view_data
    path('view-data/', views.view_data, name='view_data'),
    path('download_excel/', views.export_to_excel_view, name='download_excel'), # Kept just in case direct access needed
    
    # Habit Management
    path('habits/', views.habit_list, name='habit_list'),
    path('habits/create/', views.habit_create, name='habit_create'),
    path('habits/<int:pk>/edit/', views.habit_update, name='habit_update'),
    path('habits/<int:pk>/delete/', views.habit_delete, name='habit_delete'),

    # Quote Management
    path('quotes/create/', views.quote_create_manage, name='quote_create_manage'),
    path('quotes/<int:pk>/edit/', views.quote_update_manage, name='quote_update_manage'),
    path('quotes/<int:pk>/delete/', views.quote_delete_manage, name='quote_delete_manage'),
    path('api/reorder-quotes/', views.reorder_quotes, name='reorder_quotes'),

    path('delete-quote/<int:id>/', views.delete_quote, name='delete_quote'),
    path('api/', include(router.urls)),
    path('api/load-tasks/', views.load_tasks, name='load-tasks'),
    path('api/add-plan/', views.add_plan_api, name='add_plan_api'),
    path('api/add-branch/', views.add_branch_api, name='add_branch_api'),
    path('api/delete-plan/', views.delete_plan_api, name='delete_plan_api'),
    path('api/delete-branch/', views.delete_branch_api, name='delete_branch_api'),
]