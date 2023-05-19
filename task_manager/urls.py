from django.contrib import admin
from django.urls import include, path

from task_manager import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.Index.as_view(), name='index'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('users/', include('task_manager.users.urls')),
    path('statuses/', include('task_manager.statuses.urls')),
    path('tasks/', include('task_manager.tasks.urls')),
]
