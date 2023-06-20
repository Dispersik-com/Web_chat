from django.contrib.sessions.models import Session
from django.utils import timezone
from django.core.cache import cache

class DataMixin:
    """ Класс для получения общих данных и уменьшения количества кода"""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получить количество активных пользователей.
        # Проверяем кэш для минимизации запросов к БД.

        active_users_count = cache.get('active_users_count')
        if not active_users_count:
            active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
            active_users_count = active_sessions.count()
            cache.set('active_users_count', active_users_count, 60)
        context['active_users_count'] = active_users_count

        return context