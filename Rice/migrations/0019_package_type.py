# Generated by Django 3.1.6 on 2021-03-01 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Rice', '0018_rice_sell_check'),
    ]

    operations = [
        migrations.CreateModel(
            name='Package_Type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_name', models.CharField(max_length=16, verbose_name='包装分类名称')),
            ],
            options={
                'verbose_name': '大米分类管理',
                'verbose_name_plural': '大米分类管理',
            },
        ),
    ]
