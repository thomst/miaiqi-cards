from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopsection',
            name='description_text',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
