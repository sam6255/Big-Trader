# Generated by Django 3.1.6 on 2021-02-08 00:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Rice', '0003_auto_20210207_2345'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rice_buy_order',
            old_name='data',
            new_name='date',
        ),
        migrations.AlterField(
            model_name='rice_buy_order',
            name='get_package',
            field=models.CharField(choices=[('GOLDEN', '金包装'), ('SILVER', '银包装'), ('NORMAL', '牛皮纸')], default='NORMAL', max_length=32, verbose_name='包装种类'),
        ),
        migrations.AlterField(
            model_name='rice_buy_order',
            name='get_rice_ratio',
            field=models.CharField(choices=[('HALF', '5:5'), ('FOUR', '4:6'), ('THREE', '3:7')], default='HALF', max_length=32, verbose_name='大米比例'),
        ),
    ]