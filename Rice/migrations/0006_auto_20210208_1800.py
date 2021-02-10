# Generated by Django 3.1.6 on 2021-02-08 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Rice', '0005_rice_sell_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rice_buy_order',
            options={'verbose_name': '大米进货订单', 'verbose_name_plural': '大米进货订单'},
        ),
        migrations.AlterModelOptions(
            name='rice_sell_order',
            options={'verbose_name': '大米销售订单', 'verbose_name_plural': '大米销售订单'},
        ),
        migrations.AlterField(
            model_name='rice_sell_order',
            name='date',
            field=models.DateField(blank=True, verbose_name='日期'),
        ),
    ]
