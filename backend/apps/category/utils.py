from backend.apps.category.models import Category


def get_next_order(father_space):
    qs = Category.objects.filter(father_space=father_space).order_by('order')
    existing_orders = [0] + list(qs.values_list('order', flat=True))
    if len(existing_orders) >= 101:
        raise Exception
    for i in range(1, len(existing_orders)):
        if existing_orders[i] != i:
            return i
    return len(existing_orders)
