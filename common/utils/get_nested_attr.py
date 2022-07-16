from functools import reduce


def get_nested_attr(instance, attrs: str, default=None):
    """
    :param instance: object
    :param attrs: string of attrs separated by dot: attr1.attr2.attr3
    :param default: default
    :return:
    """
    return reduce(lambda obj, attr: getattr(obj, attr, default), attrs.split('.'), instance)