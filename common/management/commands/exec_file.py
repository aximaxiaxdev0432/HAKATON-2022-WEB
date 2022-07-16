import traceback
from django.core.management.base import BaseCommand
from os import path


class Command(BaseCommand):
    help = 'Execute file'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)

    def handle(self, *args, **options):
        if path.exists(options['path']):
            try:
                exec(open(options['path']).read())
                self.stdout.write(self.style.SUCCESS(f'Successfully execute  file "{options["path"]}"'))
            except Exception:
                print(traceback.format_exc())
                self.stdout.write(self.style.ERROR(f'Error on execute file "{options["path"]}"'))
        else:
            self.stdout.write(self.style.ERROR(f'No search file or directory "{options["path"]}"'))