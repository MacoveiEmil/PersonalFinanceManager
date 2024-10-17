from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add_transaction/', views.add_transaction, name='add_transaction'),
    path('report/', views.report, name='report'),
    path('delete_transaction/<int:id>/', views.delete_transaction, name='delete_transaction'),  # New URL

]
