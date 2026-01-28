from django.urls import path
from . import views

urlpatterns = [
    # The Finance Hub (Where the officer adds courses and sees balances)
    path('hub/', views.finance_index, name='finance_index'),
    path('course/edit/<int:pk>/', views.edit_course, name='edit_course'),
    path('course/delete/<int:pk>/', views.delete_course, name='delete_course'),
    # The Payment Page (Where the officer updates a student's balance)
    path('payment/<int:invoice_id>/', views.record_payment, name='record_payment'),
    
]