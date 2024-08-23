from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned


class GetOrNoneMixin:
    @classmethod
    def get_or_none(cls, **kwargs):
        try:
            return cls.objects.get(**kwargs)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return None