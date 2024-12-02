from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from custom_scripts.views import ScriptCreateUserView, BuyPricingOptions, PopulateProgramForClassView

urlpatterns = [
    url(r'^create/user$', ScriptCreateUserView.as_view()),
    url(r'^buy/service$', BuyPricingOptions.as_view()),
    url(r'^sync/class/program$', PopulateProgramForClassView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
