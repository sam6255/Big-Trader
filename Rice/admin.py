import datetime
from django.contrib import admin
from django.db.models.aggregates import Sum
from django.forms import widgets
from django import forms
from Rice.forms import Rice_buy_order_form
from .RawChangeList import RawChangeList
from .models import Rice_buy_order, Rice_sell_order, Rice_Bought_Check, Rice_Stock_Check, Rice_Sell_Check, Package_Type, \
    Package_Ratio

admin.site.site_header = '大米进销存后台'
admin.site.index_title = '大米进销存后台'
admin.site.site_title = '大米进销存后台'


class CustomModelPackageChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % (obj.type_name)

class Rice_Admin(admin.ModelAdmin):
    form = Rice_buy_order_form
    # 筛选条件
    list_filter = ['put_date', 'get_rice_ratio', 'get_package']
    list_display = ['id', 'put_date', 'order_amount', 'order_price', 'get_rice_ratio', 'get_package', 'get_rice_amount',
                    'lux_amount',
                    'lux_price', 'get_lux_amount', 'big_amount', 'big_price', 'get_big_amount', 'other_money',
                    'get_total_amount', 'stock_amount', 'mark']
    list_display_links = ['id']
    list_per_page = 20
    list_editable = ['order_amount', 'order_price', 'get_rice_ratio', 'get_package', 'lux_amount', 'lux_price',
                     'big_amount', 'big_price', 'other_money', 'stock_amount', 'mark']
    search_fields = ['order_amount', 'mark']


    def get_rice_amount(self, instance):
        return instance.order_amount * instance.order_price

    get_rice_amount.short_description = u"大米成本(元)"
    get_rice_amount.is_column = True
    get_rice_amount.allow_tags = True

    def get_lux_amount(self, instance):
        return instance.lux_amount * instance.lux_price

    get_lux_amount.short_description = u"精装小计(元)"
    get_lux_amount.is_column = True
    get_lux_amount.allow_tags = True

    def get_big_amount(self, instance):
        return instance.big_amount * instance.big_price

    get_big_amount.short_description = u"大包小计(元)"
    get_big_amount.is_column = True
    get_big_amount.allow_tags = True

    def get_total_amount(self, instance):
        return instance.big_amount * instance.big_price + instance.order_amount * instance.order_price + instance.lux_amount * instance.lux_price + instance.other_money

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'get_package':
            return CustomModelPackageChoiceField(queryset=Package_Type.objects.all())
        if db_field.name == 'get_rice_ratio':
            return CustomModelPackageChoiceField(queryset=Package_Ratio.objects.all())
        return super(Rice_Admin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    get_total_amount.short_description = u"成本总额(元)"
    get_total_amount.is_column = True
    get_total_amount.allow_tags = True




admin.site.register(Rice_buy_order, Rice_Admin)


class Rice_Sell_Admin(admin.ModelAdmin):
    # 筛选条件
    list_filter = ['put_date', 'get_rice_ratio', 'get_package', 'delivery_co', 'get_pay_status']
    list_display = ['id', 'put_date', 'buyer', 'delivery', 'phone', 'add', 'order_amount', 'order_price',
                    'get_rice_fee',
                    'delivery_fee', 'get_delivery_fee', 'get_total_fee', 'get_rice_ratio', 'get_package', 'package',
                    'delivery_co',
                    'sign_time', 'get_pay_status', 'mark']
    list_display_links = ['id']
    list_per_page = 20
    list_editable = ['buyer', 'delivery', 'phone', 'add', 'order_amount', 'order_price', 'delivery_fee',
                     'get_rice_ratio',
                     'get_package', 'package', 'delivery_co', 'sign_time', 'get_pay_status', 'mark']
    search_fields = ['buyer', 'phone', 'delivery', 'mark']

    # 大米费用外部计算
    # 总费用外部计算
    def get_rice_fee(self, instance):
        return instance.order_amount * instance.order_price

    get_rice_fee.short_description = u'大米费用'
    get_rice_fee.is_column = True

    def get_delivery_fee(self, instance):
        return instance.order_amount * instance.delivery_fee

    get_delivery_fee.short_description = u'运费费用'
    get_delivery_fee.is_column = True

    def get_total_fee(self, instance):
        return instance.order_amount * instance.order_price + (instance.order_amount * instance.delivery_fee)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'get_package':
            return CustomModelPackageChoiceField(queryset=Package_Type.objects.all())
        if db_field.name == 'get_rice_ratio':
            return CustomModelPackageChoiceField(queryset=Package_Ratio.objects.all())
        return super(Rice_Sell_Admin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    get_total_fee.short_description = u'全部费用'
    get_total_fee.is_column = True


admin.site.register(Rice_sell_order, Rice_Sell_Admin)

'''print('测试输出1')
test_rice=Rice_buy_order.objects.values('order_amount')
print('测试输出2')
print(test_rice[1]['order_amount'])
print('测试输出单个金额')
print(list(Rice_buy_order.objects.values()))
print('测试输出全部数量', Rice_buy_order.objects.count())
test_cccc = Rice_buy_order.objects.aggregate(numa=Sum('order_amount'))
print('测试求和', test_cccc['numa'])
today = datetime.datetime.now()
print('当前月份', today.month, today.year)
print('日期筛选', Rice_buy_order.objects.filter(put_date__year=today.year).aggregate(numa=Sum('order_amount')))'''


# 库存盘点 根据比例和包装 ratio 参数'HALF' 'FOUR' 'THREE' /package 'GOLDEN' 'SILVER' 'NORMAL'
def stock_check(ratio, package):
    stock_in = Rice_buy_order.objects.filter(get_rice_ratio=ratio, get_package=package).aggregate(
        numi=Sum('order_amount'))
    stock_out = Rice_sell_order.objects.filter(get_rice_ratio=ratio, get_package=package).aggregate(
        numo=Sum('order_amount'))
    if stock_in['numi'] == None and stock_out['numo'] != None:
        return 0 - stock_out['numo']
    elif stock_in['numi'] != None and stock_out['numo'] == None:
        return stock_in['numi'] - 0
    elif stock_in['numi'] == None and stock_out['numo'] == None:
        return 0
    else:
        return stock_in['numi'] - stock_out['numo']


# 盘点数据入库
def stock_check_admin():
    Rice_Stock_Check.objects.all().delete()
    new_check_1 = Rice_Stock_Check(stock_rice_ratio='5:5', package_type='金色装',
                                   stock_amount=stock_check('HALF', 'GOLDEN'))
    new_check_1.save()
    new_check_2 = Rice_Stock_Check(stock_rice_ratio='5:5', package_type='银色装',
                                   stock_amount=stock_check('HALF', 'SILVER'))
    new_check_2.save()
    new_check_3 = Rice_Stock_Check(stock_rice_ratio='5:5', package_type='牛皮纸',
                                   stock_amount=stock_check('HALF', 'NORMAL'))
    new_check_3.save()
    new_check_4 = Rice_Stock_Check(stock_rice_ratio='4:6', package_type='金色装',
                                   stock_amount=stock_check('FOUR', 'GOLDEN'))
    new_check_4.save()
    new_check_5 = Rice_Stock_Check(stock_rice_ratio='4:6', package_type='银色装',
                                   stock_amount=stock_check('FOUR', 'SILVER'))
    new_check_5.save()
    new_check_6 = Rice_Stock_Check(stock_rice_ratio='4:6', package_type='牛皮纸',
                                   stock_amount=stock_check('FOUR', 'NORMAL'))
    new_check_6.save()
    new_check_7 = Rice_Stock_Check(stock_rice_ratio='3:7', package_type='金色装',
                                   stock_amount=stock_check('THREE', 'GOLDEN'))
    new_check_7.save()
    new_check_8 = Rice_Stock_Check(stock_rice_ratio='3:7', package_type='银色装',
                                   stock_amount=stock_check('THREE', 'SILVER'))
    new_check_8.save()
    new_check_9 = Rice_Stock_Check(stock_rice_ratio='3:7', package_type='牛皮纸',
                                   stock_amount=stock_check('THREE', 'NORMAL'))
    new_check_9.save()


class Rice_Stock_Check_Admin(admin.ModelAdmin):
    list_display = ['get_rice_ratio', 'package_type', 'stock_amount']
    # list_display_links = ['stock_rice_ratio']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_changelist(self, request, **kwargs):
        return RawChangeList

    def get_queryset(self, request):
        return Rice_Stock_Check.objects.raw('select a.id, c.type_name get_rice_ratio,d.type_name package_type,ifnull(a.order_amount-b.order_amount, 0) stock_amount from (select id,order_amount,get_rice_ratio_id,get_package_id from Rice_rice_buy_order a group by a.get_rice_ratio_id,a.get_package_id) a left join (select id,order_amount,get_rice_ratio_id,get_package_id from Rice_rice_sell_order a group by a.get_rice_ratio_id,a.get_package_id) b on b.get_rice_ratio_id=a.get_rice_ratio_id and b.get_package_id=a.get_package_id left join Rice_package_ratio c on c.id=a.get_rice_ratio_id left join Rice_package_type d on d.id=a.get_package_id')

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == 'get_rice_ratio':
    #         return CustomModelPackageChoiceField(queryset=Package_Ratio.objects.all())
    #     return super(Rice_Stock_Check_Admin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_object(self, request, object_id, from_field=None):
        return ''
admin.site.register(Rice_Stock_Check, Rice_Stock_Check_Admin)


# *************进货统计*************

class Rice_Bought_Check_Admin(admin.ModelAdmin):
    list_display = ['check_month', 'rice_ratio', 'package_type', 'rice_money', 'lux_money', 'big_money',
                    'total_money']
    # change_list_template = 'admin/change_list.html'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_changelist(self, request, **kwargs):
        return RawChangeList

    def get_queryset(self, request):
        return Rice_Stock_Check.objects.raw('select max(a.id) id, a.put_date check_month, b.type_name rice_ratio, c.type_name package_type, sum(a.order_amount) rice_money,  sum(a.lux_amount) lux_money, sum(a.big_amount) big_money, sum(a.order_amount +a.lux_amount +  a.big_amount) total_money from Rice_rice_buy_order a join rice_package_ratio b on b.id=a.get_rice_ratio_id join rice_package_type c on c.id=a.get_package_id group by a.put_date,a.get_rice_ratio_id,a.get_package_id order by a.put_date desc')

    def get_object(self, request, object_id, from_field=None):
        return ''

admin.site.register(Rice_Bought_Check, Rice_Bought_Check_Admin)


class Rice_Sell_Check_Admin(admin.ModelAdmin):
    list_display = ['check_month', 'rice_ratio', 'package_type', 'rice_money', 'delivery_money', 'total_money']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_changelist(self, request, **kwargs):
        return RawChangeList

    def get_queryset(self, request):
        return Rice_Stock_Check.objects.raw('select max(a.id) id, a.put_date check_month, b.type_name rice_ratio, c.type_name package_type, sum(a.order_amount) rice_money,  sum(a.delivery_fee) delivery_money,  sum(a.order_amount +a.delivery_fee ) total_money from rice_rice_sell_order a join rice_package_ratio b on b.id=a.get_rice_ratio_id join rice_package_type c on c.id=a.get_package_id group by a.put_date,a.get_rice_ratio_id,a.get_package_id order by a.put_date desc')

    def get_object(self, request, object_id, from_field=None):
        return ''


admin.site.register(Rice_Sell_Check, Rice_Sell_Check_Admin)


# 定时生成报表
# def task():
#     stock_check_admin()

# 分类选择
class Package_Type_Admin(admin.ModelAdmin):
    list_display = ['id', 'type_name']
    list_display_links = ['id']
    ordering = ['id']

admin.site.register(Package_Type, Package_Type_Admin)

# 载入/刷新页面时候 加载 bought_check() stock_check_admin() sell_check()看看能不能绑定刷新按钮上
# 表格宽度调整 颜色调整
# 软删除改为真删除