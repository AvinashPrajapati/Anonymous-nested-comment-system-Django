from django.urls import path
from . import views

urlpatterns = [
    path("", views.PostIndexView.as_view(), name="post-list"),
    path("detail/<int:pk>", views.post_detail, name="post_detail"),
    path("like/<int:pk>", views.postLike, name="blog_like"),
    path("comment/reply/", views.reply_page, name="reply"),
    path("mail/", views.mailSent, name="mailSent"),
]
