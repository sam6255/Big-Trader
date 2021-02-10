# Generated by Django 3.1.6 on 2021-02-08 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Rice', '0011_auto_20210208_1807'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rice_buy_order',
            name='total_amount',
        ),
        migrations.RemoveField(
            model_name='rice_buy_order',
            name='weight_price',
        ),
        migrations.AddField(
            model_name='rice_buy_order',
            name='big_amount',
            field=models.IntegerField(blank=True, default=0, verbose_name='大件包数（件)'),
        ),
        migrations.AddField(
            model_name='rice_buy_order',
            name='big_price',
            field=models.FloatField(default=0.0, max_length=8, verbose_name='大件单价(元)'),
        ),
        migrations.AddField(
            model_name='rice_buy_order',
            name='lux_amount',
            field=models.IntegerField(blank=True, default=0, verbose_name='精装盒数量(个)'),
        ),
        migrations.AddField(
            model_name='rice_buy_order',
            name='lux_price',
            field=models.FloatField(default=0.0, max_length=8, verbose_name='精装和单价(元)'),
        ),
        migrations.AddField(
            model_name='rice_buy_order',
            name='mark',
            field=models.CharField(blank=True, max_length=32, verbose_name='备注'),
        ),
        migrations.AddField(
            model_name='rice_buy_order',
            name='other_money',
            field=models.FloatField(default=0.0, max_length=8, verbose_name='其他费用(元)'),
        ),
        migrations.AddField(
            model_name='rice_buy_order',
            name='stock_amount',
            field=models.IntegerField(blank=True, default=0.0, verbose_name='库存数量(斤)'),
        ),
        migrations.AlterField(
            model_name='rice_buy_order',
            name='date',
            field=models.DateField(auto_now_add=True, verbose_name='日期'),
        ),
        migrations.AlterField(
            model_name='rice_buy_order',
            name='order_amount',
            field=models.IntegerField(blank=True, default=0, verbose_name='数量(斤)'),
        ),
        migrations.AlterField(
            model_name='rice_buy_order',
            name='order_price',
            field=models.FloatField(blank=True, default=0, verbose_name='单价(元)'),
        ),
        migrations.AlterField(
            model_name='rice_sell_order',
            name='sign_time',
            field=models.DateField(blank=True, default=models.DateField(auto_now_add=True, verbose_name='日期'), verbose_name='签收日期'),
        ),
    ]
