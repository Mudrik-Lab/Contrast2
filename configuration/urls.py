from django.urls import path, include
from rest_framework_nested import routers

from configuration.views import ConfigurationView

router = routers.SimpleRouter()

router.register(r'configuration', ConfigurationView, basename="configuration")


urlpatterns = [
    path('', include(router.urls)),

]
