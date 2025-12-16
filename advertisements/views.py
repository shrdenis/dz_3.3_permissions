from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from advertisements.filters import AdvertisementFilter
from advertisements.models import Advertisement, Favorite, AdvertisementStatusChoices
from advertisements.serializers import AdvertisementSerializer


class IsOwnerOrAdmin(permissions.BasePermission):
    """Разрешение на изменение/удаление для автора или админа."""

    message = "Объявление может менять только его автор или администратор."

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            obj.creator == user
            or user.is_staff
            or user.is_superuser
        )

class AdvertisementViewSet(ModelViewSet):
    """ViewSet для объявлений."""

    queryset = Advertisement.objects.all().order_by("-created_at")
    serializer_class = AdvertisementSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AdvertisementFilter
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action == "create":
            return [IsAuthenticated()]
        if self.action in ["favorite", "favorites"]:
            return [IsAuthenticated()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsOwnerOrAdmin()]
        return []

    def get_queryset(self):
        """Скрываем черновики от чужих пользователей."""
        queryset = Advertisement.objects.all().order_by("-created_at")
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return queryset
        if user.is_authenticated:
            return queryset.filter(~Q(status=AdvertisementStatusChoices.DRAFT) | Q(creator=user))
        return queryset.exclude(status=AdvertisementStatusChoices.DRAFT)

    @action(detail=True, methods=["post", "delete"], url_path="favorite")
    def favorite(self, request, pk=None):
        """Добавление/удаление объявления из избранного текущего пользователя."""
        advertisement = self.get_object()
        user = request.user

        if request.method == "POST":
            if advertisement.creator == user:
                raise ValidationError("Автор не может добавить своё объявление в избранное.")

            Favorite.objects.get_or_create(advertisement=advertisement, user=user)
            serializer = self.get_serializer(advertisement)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        Favorite.objects.filter(advertisement=advertisement, user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="favorites")
    def favorites(self, request):
        """Список объявлений, добавленных в избранное текущим пользователем."""
        queryset = self.filter_queryset(
            self.get_queryset().filter(favorites__user=request.user).distinct()
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
