from django.contrib.auth.models import User
from rest_framework import serializers

from advertisements.models import Advertisement, AdvertisementStatusChoices, Favorite


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'created_at', 'is_favorited')

    def create(self, validated_data):
        """Метод для создания"""

        # Простановка значения поля создатель по-умолчанию.
        # Текущий пользователь является создателем объявления
        # изменить или переопределить его через API нельзя.
        # обратите внимание на `context` – он выставляется автоматически
        # через методы ViewSet.
        # само поле при этом объявляется как `read_only=True`
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""

        request = self.context.get("request")
        user = getattr(request, "user", None)
        creator = self.instance.creator if self.instance else user

        new_status = data.get(
            "status",
            self.instance.status if self.instance else AdvertisementStatusChoices.OPEN
        )

        if (
            new_status == AdvertisementStatusChoices.OPEN
            and creator
            and not creator.is_anonymous
        ):
            open_ads = Advertisement.objects.filter(
                creator=creator,
                status=AdvertisementStatusChoices.OPEN,
            )
            if self.instance:
                open_ads = open_ads.exclude(pk=self.instance.pk)
            if open_ads.count() >= 10:
                raise serializers.ValidationError(
                    "Превышено максимальное количество открытых объявлений (10)."
                )

        return data

    def get_is_favorited(self, obj):
        """Флаг, добавлено ли объявление в избранное текущего пользователя."""
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        return Favorite.objects.filter(advertisement=obj, user=user).exists()
