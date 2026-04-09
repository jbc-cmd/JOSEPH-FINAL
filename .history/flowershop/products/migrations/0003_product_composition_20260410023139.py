from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_productreview_user_photo_and_rating_refresh'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='composition',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]
