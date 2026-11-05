import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('postcards', '0013_delete_postcardpage'),
        ('responsive_image', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postcard',
            name='image',
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='postcard',
                to='responsive_image.image',
            ),
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(
                    name='Image',
                ),
            ],
        ),
    ]
