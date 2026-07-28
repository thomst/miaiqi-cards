import os
from django.core.management.base import BaseCommand
from ..utils import ImagePathsMixin


class Command(BaseCommand, ImagePathsMixin):
    help = 'Delete leftover postcard images.'

    def handle(self, *args, **options):
        leftover = self.leftover_files
        if not leftover:
            self.stdout.write('No leftover files found.')
            return

        self.stdout.write('Leftover files:')
        for path in leftover:
            self.stdout.write(f'  {path}')

        confirm = input('Delete these files? [y/N]: ').strip().lower()
        if confirm not in ('y', 'yes'):
            self.stdout.write('Aborted. No files were deleted.')
            return

        deleted = 0
        for path in leftover:
            try:
                os.remove(path)
                deleted += 1
                self.stdout.write(f'Deleted: {path}')
            except FileNotFoundError:
                self.stdout.write(f'Not found (skipped): {path}')
            except PermissionError:
                self.stdout.write(f'Permission denied (skipped): {path}')
            except Exception as e:
                self.stdout.write(f'Error deleting {path}: {e}')

        self.stdout.write(f'Done. {deleted} files deleted.')
