from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_product_composition'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flower',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='flowers/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='products/'),
        ),
    ]
