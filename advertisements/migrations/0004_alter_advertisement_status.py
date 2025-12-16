# Generated manually to add DRAFT status choice
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advertisements', '0003_favorite'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advertisement',
            name='status',
            field=models.TextField(choices=[('OPEN', 'Открыто'), ('CLOSED', 'Закрыто'), ('DRAFT', 'Черновик')], default='OPEN'),
        ),
    ]
