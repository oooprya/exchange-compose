from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wholesale", "0006_alter_wholesaleorder_order_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="wholesaleorder",
            name="collection_items",
            field=models.JSONField(
                blank=True,
                default=list,
                verbose_name="Состав инкассации",
            ),
        ),
    ]
