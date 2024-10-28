from django.urls import path
from .views import add_comment
from . import views
from .views import *
from .views import register_view, verify_otp

urlpatterns = [
    path('register/', register_view, name='register_view'),
    path('register/see-blog/', views.see_blog, name='see_blog'),
    path('verify/<token>/', verify_otp, name='verify'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('', home, name="home"),
    path('home/', home, name="home_view"),
    path('login/', login_view, name="login_view"),
    path('add-blog/', add_blog, name="add_blog"),
    path('blog-detail/<slug>', blog_detail, name="blog_detail"),
    path('see-blog/', see_blog, name="see_blog"),
    path('blog-delete/<id>', blog_delete, name="blog_delete"),
    path('blog-update/<slug>/', blog_update, name="blog_update"),
    path('logout-view/', logout_view, name="logout_view"),
    path('blog/', see_blog, name="blog"),
    # Comment submission URL
    path('add_comment/', add_comment, name="add_comment"),  # Add this line for the comment section
    path('add-comment/<slug>/', add_comment, name="add_comment")
]
