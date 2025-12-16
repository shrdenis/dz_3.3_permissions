from django_filters import rest_framework as filters

from advertisements.models import Advertisement


class AdvertisementFilter(filters.FilterSet):
    """Фильтры для объявлений."""

    created_at = filters.DateFromToRangeFilter()
    status = filters.CharFilter()
    is_favorited = filters.BooleanFilter(method="filter_is_favorited")

    class Meta:
        model = Advertisement
        fields = ["created_at", "status", "is_favorited"]

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрация по избранным для текущего пользователя."""
        if not value:
            return queryset

        user = getattr(self.request, "user", None)
        if not user or not user.is_authenticated:
            return queryset.none()

        return queryset.filter(favorites__user=user).distinct()
