from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('delete-food/<int:item_id>/', views.delete_food_view, name='delete_food'), # Delete Line
    path('add-food/<int:food_id>/', views.add_food_from_search, name='add_food_from_search'),
    path('delete-food/<int:item_id>/', views.delete_food_view, name='delete_food'),
    path('add-api-food/', views.add_food_from_api, name='add_food_from_api'),
]