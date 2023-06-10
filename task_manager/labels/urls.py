from django.urls import path

from task_manager.labels.views import (
    CreateLabelView,
    DeleteLabelView,
    LabelsListView,
    UpdateLabelView,
)

urlpatterns = [
    path('', LabelsListView.as_view(), name='labels_list'),
    path('create/', CreateLabelView.as_view(), name='create_label'),
    path('<int:pk>/update/', UpdateLabelView.as_view(), name='update_label'),
    path('<int:pk>/delete/', DeleteLabelView.as_view(), name='delete_label'),
]
