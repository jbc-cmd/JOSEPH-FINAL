from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_bouquet', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bouquet',
            name='custom_flower_count',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='bouquet',
            name='is_custom_size',
            field=models.BooleanField(default=False),
        ),
    ]
