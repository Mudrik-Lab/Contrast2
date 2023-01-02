from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save


def setup_profile(sender, instance, created, **kwargs):
    # Imported here because else it would run before the models are ready
    from users.models import Profile

    if created:
        Profile.objects.create(user=instance)


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        post_save.connect(receiver=setup_profile, sender=get_user_model())
