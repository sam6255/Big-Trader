# Generated by Django 3.1.5 on 2021-04-03 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Rice', '0026_auto_20210403_1507'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package_ratio',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='package_type',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
