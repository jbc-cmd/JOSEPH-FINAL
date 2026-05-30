from django.contrib.staticfiles.storage import staticfiles_storage


PRODUCT_IMAGE_FALLBACKS = {
    'anniversary-glory': 'images/products/Anniversary.png',
    'birthday-blast': 'images/products/Birthday_Blast.png',
    'blushing-petals': 'images/products/Blushing_Petals.png',
    'crimson-romance': 'images/products/Crimson_Romance.png',
    'grad-star': 'images/products/Grad_Star.png',
    'royal-elegance': 'images/products/Royal_Elegance.png',
    'sunshine-delight': 'images/products/Sunshine_Delight.png',
    'wildflower-dream': 'images/products/Wildflower_Dream.png',
}

FLOWER_IMAGE_FALLBACKS = {
    'ASTROMERIA': 'images/flowers/Alstroemeria.jpg',
    'BANGKOK': 'images/flowers/Bankok_Yellow.png',
    'CARNATION': 'images/flowers/Carnation.jpg',
    'GERBERA': 'images/flowers/gerbera.png',
    'GLADIOLA': 'images/flowers/Gladiola.png',
    'GYPSOPHYLLA': 'images/flowers/Gypsophila.png',
    'JAGUAR': 'images/flowers/jaguar_purple.png',
    'JIMBA': 'images/flowers/jimba.png',
    'MISTY': 'images/flowers/Misty_blue.png',
    'MUM': 'images/flowers/Malaysian_moms.png',
    'ROSE': 'images/flowers/Roses.png',
    'STARGAZER': 'images/flowers/Stargazer.png',
    'STATICE': 'images/flowers/Statice.png',
    'SUNFLOWER': 'images/flowers/Sunflower.png',
}


def _stored_image_url(image_field):
    if not image_field:
        return ''
    try:
        return image_field.url
    except ValueError:
        return ''


def product_image_url(product):
    image_url = _stored_image_url(getattr(product, 'image', None))
    if image_url:
        return image_url

    fallback_path = PRODUCT_IMAGE_FALLBACKS.get(getattr(product, 'slug', ''))
    return staticfiles_storage.url(fallback_path) if fallback_path else ''


def flower_image_url(flower):
    image_url = _stored_image_url(getattr(flower, 'image', None))
    if image_url:
        return image_url

    fallback_path = FLOWER_IMAGE_FALLBACKS.get(getattr(flower, 'name', ''))
    return staticfiles_storage.url(fallback_path) if fallback_path else ''
