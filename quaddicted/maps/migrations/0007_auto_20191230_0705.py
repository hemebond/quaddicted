# Generated by Django 3.0.1 on 2019-12-30 07:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('maps', '0006_auto_20191230_0315'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentFlag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.RemoveField(
            model_name='review',
            name='comment',
        ),
        migrations.RemoveField(
            model_name='review',
            name='created_date',
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_name', models.CharField(blank=True, max_length=32, null=True)),
                ('comment', models.TextField()),
                ('map', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='maps.Map')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]