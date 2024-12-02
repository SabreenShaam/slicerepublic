from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken import views
from accounts.views import TokenView, GetUser, Logout, MemberAgreementView, AppVersionView, RequiredFieldList, \
    UserSignupView, UsersSearchView, VerificationEmailView, UserPasswordResetView, MboClientSettingView, GetUserList

urlpatterns = [
    url(r'^api/auth/token', views.obtain_auth_token),
    url(r'^api/token', TokenView.as_view()),
    url(r'^api/user$', GetUser.as_view()),
    url(r'^api/logout', Logout.as_view()),
    url(r'^api/member-agreement', MemberAgreementView.as_view()),
    url(r'^api/app/(?P<platform>.*)/version', AppVersionView.as_view()),
    url(r'^api/(?P<pk>\d+)/studio/required-fields', RequiredFieldList.as_view()),
    url(r'^api/signup/user', UserSignupView.as_view()),
    url(r'^api/users/search$', UsersSearchView.as_view()),
    url(r'^api/user/email/verify', VerificationEmailView.as_view()),
    url(r'^api/user/change-password', UserPasswordResetView.as_view()),
    url(r'^api/client/setting', MboClientSettingView.as_view()),
    url(r'^api/users$', GetUserList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
