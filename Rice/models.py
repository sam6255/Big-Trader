from django.db import models
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
import datetime


class Rice_buy_order(models.Model):

    class Meta:
        verbose_name = u"大米进货订单"
        verbose_name_plural = u"大米进货订单"

    put_date = models.DateField(verbose_name="日期", blank=True, auto_now_add=True)
    order_amount = models.IntegerField(verbose_name='数量(斤)', blank=True, default=0)
    order_price = models.FloatField(verbose_name='单价(元)', blank=True, default=0)
    get_package = models.ForeignKey("Package_Type", on_delete=models.CASCADE, default=3, verbose_name='包装种类')
    get_rice_ratio = models.ForeignKey("Package_Ratio", on_delete=models.CASCADE, default=1, verbose_name='大米比例')

    def get_money(order_amount):
        return order_amount

    # 大米成本价格元
    lux_amount = models.IntegerField(verbose_name='精装盒数量(个)', blank=True, default=0)
    lux_price = models.FloatField(verbose_name='精装和单价(元)', max_length=8, default=0.0)
    # 精装盒费用小计元
    big_amount = models.IntegerField(verbose_name='大件包数（件)', blank=True, default=0)
    big_price = models.FloatField(verbose_name='大件单价(元)', max_length=8, default=0.0)
    # 大包费用小计元
    other_money = models.FloatField(verbose_name='其他费用(元)', max_length=8, default=0.0)
    # 成本总额元
    stock_amount = models.IntegerField(verbose_name='库存数量(斤)', blank=True, default=0.0)
    mark = models.CharField(verbose_name='备注', max_length=32, blank=True)
    # 大米包装进货测试

    def __reduce__(self):
        return '增加进货订单成功'


class Rice_sell_order(models.Model):
    put_date = models.DateField(verbose_name="日期", blank=True, auto_now_add=True)
    buyer = models.CharField(verbose_name='购买人', max_length=8, blank=True)
    delivery = models.CharField(verbose_name='收货人', max_length=8, blank=True)
    phone = models.CharField(verbose_name='收货人电话', max_length=16, blank=True)
    add = models.CharField(verbose_name='收货地址', max_length=32, blank=True)
    order_amount = models.IntegerField(verbose_name='数量(斤)', blank=True, default=0)
    order_price = models.FloatField(verbose_name='单价(元)', blank=True, default=0)
    get_package = models.ForeignKey("Package_Type", on_delete=models.CASCADE, default=3, verbose_name='包装种类')
    get_rice_ratio = models.ForeignKey("Package_Ratio", on_delete=models.CASCADE, default=1, verbose_name='大米比例')

# 大米费用外部计算
    delivery_fee = models.FloatField(verbose_name='运费(元/斤)', blank=True, default=0)
    # 总费用外部计算

    package = models.FloatField(verbose_name='件数(个)', blank=True, default=0)
    delivery_co = models.CharField(verbose_name='发货物流', max_length=8, blank=True)
    sign_time = models.DateField(verbose_name='签收日期', blank=True, default=put_date)

    class PAY_STATUS(models.TextChoices):
        PAIED = 'PAIED', _('已付款')
        UNPAY = 'UNPAY', _('未付款')

    get_pay_status = models.CharField(
        max_length=32,
        choices=PAY_STATUS.choices,
        default=PAY_STATUS.UNPAY,
        verbose_name='付款状态',
    )

    mark = models.CharField(verbose_name='备注', max_length=32, blank=True)

    class Meta:
        verbose_name = u"大米销售订单"
        verbose_name_plural = u"大米销售订单"

    def __reduce__(self):
        return '增加出货订单成功'


class Rice_Bought_Check(models.Model):
    check_month = models.CharField(verbose_name='月份', max_length=8, blank=True)
    rice_ratio = models.CharField(verbose_name='大米比例', max_length=8, blank=True)
    package_type = models.CharField(verbose_name='包装', max_length=8, blank=True)
    rice_money = models.FloatField(verbose_name='大米费用小计', blank=True, default=0)
    lux_money = models.FloatField(verbose_name='精装盒小计', blank=True, default=0)
    big_money = models.FloatField(verbose_name='大包费用小计', blank=True, default=0)
    total_money = models.FloatField(verbose_name='成本总额', blank=True, default=0)

    class Meta:
        verbose_name = u"进货报表"
        verbose_name_plural = u"进货报表"

class Rice_Stock_Check(models.Model):
    package_type = models.CharField(verbose_name='包装种类', max_length=9, blank=True)
    stock_amount = models.IntegerField(verbose_name='库存剩余', default=0)
    get_rice_ratio = models.CharField(verbose_name='大米比例', max_length=9, default=1)

    class Meta:
        verbose_name = u"库存盘点"
        verbose_name_plural = u"库存盘点"

class Rice_Sell_Check(models.Model):
    check_month = models.CharField(verbose_name='月份', max_length=8, blank=True)
    rice_ratio = models.CharField(verbose_name='大米比例', max_length=8, blank=True)
    package_type = models.CharField(verbose_name='包装', max_length=8, blank=True)
    rice_money = models.FloatField(verbose_name='大米费用小计', blank=True, default=0)
    delivery_money = models.FloatField(verbose_name='精装盒小计', blank=True, default=0)
    total_money = models.FloatField(verbose_name='成本总额', blank=True, default=0)

    class Meta:
        verbose_name = u"销售报表"
        verbose_name_plural = u"销售报表"

class Package_Type(models.Model):
    type_name = models.CharField(verbose_name='包装分类名称',max_length=16,blank=False)

    class Meta:
        verbose_name = u"大米分类管理"
        verbose_name_plural = u"大米分类管理"

class Package_Ratio(models.Model):
    type_name = models.CharField(verbose_name='包装尺寸',max_length=16,blank=False)

    class Meta:
        verbose_name = u"大米包装尺寸管理"
        verbose_name_plural = u"大米包装尺寸管理"