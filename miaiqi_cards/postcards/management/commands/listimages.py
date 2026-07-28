from django.core.management.base import BaseCommand
from ..utils import ImagePathsMixin


class Command(ImagePathsMixin, BaseCommand):
    help = "Print image paths."

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '-a', '--all',
            action='store_true',
            help='List all database-referenced and extra filesystem image files.',
        )
        group.add_argument(
            '-e', '--existing',
            action='store_true',
            help='List existing image files referenced by the database.',
        )
        group.add_argument(
            '-m', '--missing',
            action='store_true',
            help='List database-referenced image files that are missing on disk.',
        )
        group.add_argument(
            '-l', '--leftover',
            action='store_true',
            help='List image files found on disk that are not referenced by the database.',
        )

    def handle(self, *args, **options):
        use_default = not any([options[o] for o in ['all', 'existing', 'missing', 'leftover']])

        if options['all'] or use_default:
            if self.existing_files:
                self.stdout.write('\nExisting files:')
                for path in self.existing_files:
                    self.stdout.write(path)

            if self.missing_files:
                self.stdout.write('\nMissing files:')
                for path in self.missing_files:
                    self.stdout.write(path)

            if self.leftover_files:
                self.stdout.write('\nLeftover files:')
                for path in self.leftover_files:
                    self.stdout.write(path)
            return

        if options['missing']:
            for path in self.missing_files:
                self.stdout.write(path)
            return

        if options['leftover']:
            for path in self.leftover_files:
                self.stdout.write(path)
            return

        if options['existing']:
            for path in self.existing_files:
                self.stdout.write(path)
            return
