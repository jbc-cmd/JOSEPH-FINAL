from django import template

from products.image_fallbacks import flower_image_url, product_image_url, stored_image_url

register = template.Library()


@register.simple_tag
def product_image(product):
    return product_image_url(product)


@register.simple_tag
def flower_image(flower):
    return flower_image_url(flower)


@register.simple_tag
def image_url(image_field):
    return stored_image_url(image_field)
