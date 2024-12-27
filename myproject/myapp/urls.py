from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.product_list, name='product_list'),  # Product List Route
    path('flask-students/', views.get_flask_students, name='flask_students'),
    path('flask-students/<int:student_id>/', views.get_flask_student_by_id, name='flask_student_by_id'),
    path('add_student/', views.add_student, name='add_student'),
    path('update_student/<int:student_id>/', views.update_student, name='update_student'),
    path('', views.student_list, name='student_list'),  # This is the URL for the student list
    path('delete_student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('chatgpt/', views.chatgpt_text_generation, name='chatgpt_text_generation'),
    path('chatgpt-chat/', views.chatgpt_chat, name='chatgpt_chat'),
    path('chatgpt-chat-api/', views.chatgpt_api, name='chatgpt_chat_api'),
]

