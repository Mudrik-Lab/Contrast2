from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Load historic data'

    def handle(self, *args, **options):
        print("hey there")

