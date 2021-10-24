# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Watermark",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("name", models.CharField(max_length=50, verbose_name="name")),
                ("image", models.ImageField(upload_to=b"watermarks", verbose_name="image")),
                ("is_active", models.BooleanField(default=True, verbose_name="is active")),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                ("date_updated", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["name"],
                "verbose_name": "watermark",
                "verbose_name_plural": "watermarks",
            },
        ),
    ]
