import miaiqi_cards.responsive_image.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name='Image',
                    fields=[
                        (
                            'id',
                            models.BigAutoField(
                                auto_created=True,
                                primary_key=True,
                                serialize=False,
                                verbose_name='ID',
                            ),
                        ),
                        (
                            'name',
                            models.CharField(
                                blank=True,
                                max_length=100,
                                unique=True,
                            ),
                        ),
                        (
                            'original',
                            models.ImageField(
                                storage=miaiqi_cards.responsive_image.models.OverwriteStorage(),
                                upload_to=miaiqi_cards.responsive_image.models.upload_original,
                            ),
                        ),
                        (
                            'large',
                            models.ImageField(
                                storage=miaiqi_cards.responsive_image.models.OverwriteStorage(),
                                upload_to=miaiqi_cards.responsive_image.models.upload_large,
                            ),
                        ),
                        (
                            'medium',
                            models.ImageField(
                                storage=miaiqi_cards.responsive_image.models.OverwriteStorage(),
                                upload_to=miaiqi_cards.responsive_image.models.upload_medium,
                            ),
                        ),
                        (
                            'small',
                            models.ImageField(
                                storage=miaiqi_cards.responsive_image.models.OverwriteStorage(),
                                upload_to=miaiqi_cards.responsive_image.models.upload_small,
                            ),
                        ),
                    ],
                    options={
                        'db_table': 'postcards_image',
                    },
                ),
            ],
        ),
    ]
