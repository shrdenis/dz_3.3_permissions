# Generated manually for favorites feature
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('advertisements', '0002_alter_advertisement_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('advertisement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='advertisements.advertisement')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_advertisements', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'constraints': [
                    models.UniqueConstraint(fields=('user', 'advertisement'), name='unique_user_advertisement_favorite'),
                ],
            },
        ),
    ]
