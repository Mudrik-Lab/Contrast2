from django.urls import path, include
from rest_framework_nested import routers

from users.views import ProfilesView

router = routers.SimpleRouter()

router.register(r'profiles', ProfilesView, basename="profiles")


urlpatterns = [
    path('', include(router.urls)),

]
