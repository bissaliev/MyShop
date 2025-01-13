from .cart import Cart


def cart(request):
    """Корзина"""
    return {"cart": Cart(request)}
