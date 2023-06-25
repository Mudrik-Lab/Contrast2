from django.urls import path, include
from rest_framework_nested import routers

from users.views.profiles import ProfilesView
from users.views.feedback import FeedbackView

router = routers.SimpleRouter()

router.register(r'profiles', ProfilesView, basename="profiles")
router.register(r'feedbacks', FeedbackView, basename="feedback")

urlpatterns = [
    path('', include(router.urls)),

]
