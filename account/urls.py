from django.urls import path,reverse_lazy
from . import views
from django.contrib.auth import views as auth_view


app_name='account'
urlpatterns=[
    #path('login/', views.user_login,name='login'),
    path('login/',auth_view.LoginView.as_view(), name='login'),
    path('logout/',auth_view.LogoutView.as_view(), name='logout'),
    path('',views.dashboard, name='dashboard'),
    path('password_change/',auth_view.PasswordChangeView.as_view(success_url=reverse_lazy('account:password_change_done')), name='password_change'),
    path('password_change/done/',auth_view.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password_reset/',auth_view.PasswordResetView.as_view(success_url=reverse_lazy('account:password_reset_done')), name='password_reset'),
    path('password_reset/done/',auth_view.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_view.PasswordResetConfirmView.as_view(success_url=reverse_lazy('account:password_reset_complete')), name='password_reset_confirm'),
    path('reset/done/',auth_view.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('register/',views.register, name='register'),
    path('edit/',views.edit_profile, name='edit'),
    path('users/follow/',views.user_follow, name='user_follow'),
    path('users/<username>/',views.user_detail, name='user_detail'),
    path('users/',views.user_list, name='users_list'),
]
