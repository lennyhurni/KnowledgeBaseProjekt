from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_document, name='upload_document'),
    path('delete/<int:document_id>/', views.delete_document, name='delete_document'),
    path('create_folder/', views.create_folder, name='create_folder'),
    path('detail/<int:document_id>/', views.document_detail, name='document_detail'),
    path('', views.document_list, name='document_list'),
]