from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def refresh_product_review_stats(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    ProductReview = apps.get_model('products', 'ProductReview')

    for product in Product.objects.all():
        approved_reviews = ProductReview.objects.filter(product=product, is_approved=True)
        review_count = approved_reviews.count()
        if review_count:
            average_rating = sum(review.rating for review in approved_reviews) / review_count
        else:
            average_rating = 0
        product.rating = round(average_rating, 1)
        product.review_count = review_count
        product.save(update_fields=['rating', 'review_count', 'updated_at'])


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='productreview',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='review_photos/'),
        ),
        migrations.AddField(
            model_name='productreview',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_reviews', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RunPython(refresh_product_review_stats, migrations.RunPython.noop),
    ]
