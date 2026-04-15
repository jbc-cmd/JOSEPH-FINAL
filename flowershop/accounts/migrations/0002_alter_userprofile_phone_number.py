from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='phone_number',
            field=models.CharField(
                blank=True,
                max_length=17,
                validators=[
                    django.core.validators.RegexValidator(
                        regex=r'^\+?1?\d{9,15}$',
                        message='Phone number must be entered in the format: 09124169887. Up to 15 digits allowed.',
                    )
                ],
            ),
        ),
    ]
