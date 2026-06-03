from django.urls import path
from recommendor.views import *

urlpatterns = [
    path('',home , name="home"),
    path('signup',signup_view, name="signup"),
    path('predict',predict_view,name="predict"),
    path('logout' ,logout_view,name="logout"),
    path('login', login_view, name="login"),
    path('user_history',user_history_view,name="user_history"),
    path('history_delete/<int:id>/',user_delete_prediction,name="user_delete_prediction"),
    path('profile',profile_view,name="profile"),
    path('change_pass',change_view,name="change"),
    path('admin_login',admin_view,name="admin"),
    path('dashboard',dashboard_view,name="dashboard"),
    path('displayuser',displayuser_view,name="displayuser"),
    path('user_delete/<int:id>/',admin_user_delete,name="admin_user_delete"),
    path('adminprediction',adminprediction_view,name="adminprediction"),
    path('admin_prediction_delete/<int:id>/',admin_prediction_delete,name="admin_prediction_delete"),
    path('admin_logout' ,admin_logout_view,name="adminlogout"),

]