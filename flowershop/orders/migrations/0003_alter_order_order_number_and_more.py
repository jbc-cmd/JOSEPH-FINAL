from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_order_cancellation_request_reason_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_number',
            field=models.CharField(db_index=True, editable=False, max_length=32, unique=True),
        ),
        migrations.AlterField(
            model_name='ordertracking',
            name='track_by_order_number',
            field=models.CharField(max_length=32, unique=True),
        ),
    ]
