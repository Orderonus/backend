from typing import Optional
from django.contrib.auth.models import User
from .models import Store


def get_store(user: User, store_id: int) -> Optional[Store]:
    try:
        return Store.objects.get(id=store_id, user=user)
    except Store.DoesNotExist:
        return None
