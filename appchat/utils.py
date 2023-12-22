from django.contrib.sessions.models import Session
from django.utils import timezone
from django.core.cache import cache

class DataMixin:
    """ Клас для отримання загальних даних та зменшення кількості коду"""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Отримати кількість активних користувачів.
        # Перевіряємо кеш для мінімізації запитів до БД.

        active_users_count = cache.get('active_users_count')
        if not active_users_count:
            active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
            active_users_count = active_sessions.count()
            cache.set('active_users_count', active_users_count, 60)
        context['active_users_count'] = active_users_count

        return context
