import datetime
from django.contrib import admin
from django.db.models.aggregates import Sum
from django.forms import widgets
from Rice.forms import Rice_buy_order_form
from .models import Rice_buy_order, Rice_sell_order, Rice_Bought_Check, Rice_Stock_Check, Rice_Sell_Check

admin.site.site_header = '大米进销存后台'
admin.site.index_title = '大米进销存后台'
admin.site.site_title = '大米进销存后台'


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

    get_total_amount.short_description = u"成本总额(元)"
    get_total_amount.is_column = True
    get_total_amount.allow_tags = True




admin.site.register(Rice_buy_order, Rice_Admin)


class Rice_Sell_Admin(admin.ModelAdmin):
    # 筛选条件
    list_filter = ['put_date', 'get_rice_ratio', 'get_package', 'delivery_co', 'get_pay_status']
    list_display = ['put_date', 'buyer', 'delivery', 'phone', 'add', 'order_amount', 'order_price',
                    'get_rice_fee',
                    'delivery_fee', 'get_delivery_fee', 'get_total_fee', 'get_rice_ratio', 'get_package', 'package',
                    'delivery_co',
                    'sign_time', 'get_pay_status', 'mark']
    list_display_links = ['put_date']
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
    list_display = ['stock_rice_ratio', 'package_type', 'stock_amount']
    list_display_links = ['stock_rice_ratio']
    list_per_page = 20
    ordering = ['id']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Rice_Stock_Check, Rice_Stock_Check_Admin)


# *************进货统计*************
# 进货部分 根据大米比例 计算本月/上月大米费用统计 大米比例参数 'HALF' 'FOUR' 'THREE' 本月/上月'THIS'/'LAST'
def get_in_month_rice_money(ratio, package, time):
    if time == 'THIS':
        this_time = datetime.datetime.now()
        this_month_order_amount = Rice_buy_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                                put_date__year=this_time.year,
                                                                put_date__month=this_time.month).values('order_amount')
        this_month_order_price = Rice_buy_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                               put_date__year=this_time.year,
                                                               put_date__month=this_time.month).values('order_price')
        order_count = Rice_buy_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                    put_date__year=this_time.year,
                                                    put_date__month=this_time.month).count()
        # print('订单情况', this_month_order_amount, '订单数', order_count,'订单金额', this_month_order_price)
        this_month_rice_money = 0
        for number in range(0, order_count):
            this_month_rice_money += this_month_order_amount[number]['order_amount'] * this_month_order_price[number][
                'order_price']
            # print('计算金额结果', number, '次', this_month_rice_money)
        return this_month_rice_money
    elif time == 'LAST':
        this_time = datetime.datetime.now()
        if this_time.month != 1:
            this_month_order_amount = Rice_buy_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                                    put_date__year=this_time.year,
                                                                    put_date__month=this_time.month - 1).values(
                'order_amount')
            this_month_order_price = Rice_buy_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                                   put_date__year=this_time.year,
                                                                   put_date__month=this_time.month - 1).values(
                'order_price')
            order_count = Rice_buy_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                        put_date__year=this_time.year,
                                                        put_date__month=this_time.month - 1).count()
            # print('订单情况', this_month_order_amount, '订单数', order_count, '订单金额', this_month_order_price)
            this_month_rice_money = 0
            for number in range(0, order_count):
                this_month_rice_money += this_month_order_amount[number]['order_amount'] * \
                                         this_month_order_price[number]['order_price']
                # print('计算金额结果', number, '次', this_month_rice_money)
            return this_month_rice_money
        else:
            this_month_order_amount = Rice_buy_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                                    put_date__year=this_time.year - 1,
                                                                    put_date__month=12).values(
                'order_amount')
            this_month_order_price = Rice_buy_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                                   put_date__year=this_time.year - 1,
                                                                   put_date__month=12).values(
                'order_price')
            order_count = Rice_buy_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                        put_date__year=this_time.year - 1,
                                                        put_date__month=12).count()
            # print('订单情况', this_month_order_amount, '订单数', order_count, '订单金额', this_month_order_price)
            this_month_rice_money = 0
            for number in range(0, order_count):
                this_month_rice_money += this_month_order_amount[number]['order_amount'] * \
                                         this_month_order_price[number]['order_price']
                # print('计算金额结果', number, '次', this_month_rice_money)
            return this_month_rice_money
    else:
        return 0


# 进货部分 根据大米比例 计算本月/上月 精包装 包装参数 'GOLDEN' 'SILVER' 'NORMAL' 本月/上月'THIS'/'LAST'
def get_in_month_package_money(ratio, package, time):
    if time == 'THIS':
        this_time = datetime.datetime.now()
        this_month_lux_amount = Rice_buy_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                              put_date__year=this_time.year,
                                                              put_date__month=this_time.month).values('lux_amount')
        this_month_lux_price = Rice_buy_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                             put_date__year=this_time.year,
                                                             put_date__month=this_time.month).values('lux_price')
        order_count = Rice_buy_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                    put_date__year=this_time.year,
                                                    put_date__month=this_time.month).count()
        # print('订单情况', this_month_lux_amount, '订单数', order_count,'订单金额', this_month_lux_price)
        this_month_package_money = 0
        for number in range(0, order_count):
            this_month_package_money += this_month_lux_amount[number]['lux_amount'] * this_month_lux_price[number][
                'lux_price']
            # print('计算金额结果', number, '次', this_month_package_money)
        return this_month_package_money
    elif time == 'LAST':
        this_time = datetime.datetime.now()
        if this_time.month != 1:
            this_month_lux_amount = Rice_buy_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                                  put_date__year=this_time.year,
                                                                  put_date__month=this_time.month - 1).values(
                'lux_amount')
            this_month_lux_price = Rice_buy_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                                 put_date__year=this_time.year,
                                                                 put_date__month=this_time.month - 1).values(
                'lux_price')
            order_count = Rice_buy_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                        put_date__year=this_time.year,
                                                        put_date__month=this_time.month - 1).count()
            # print('订单情况', this_month_lux_amount, '订单数', order_count, '订单金额', this_month_lux_price)
            this_month_package_money = 0
            for number in range(0, order_count):
                this_month_package_money += this_month_lux_amount[number]['lux_amount'] * \
                                            this_month_lux_price[number]['lux_price']
                # print('计算金额结果', number, '次', this_month_package_money)
            return this_month_package_money
        else:
            this_month_lux_amount = Rice_buy_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                                  put_date__year=this_time.year - 1,
                                                                  put_date__month=12).values(
                'lux_amount')
            this_month_lux_price = Rice_buy_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                                 put_date__year=this_time.year - 1,
                                                                 put_date__month=12).values(
                'lux_price')
            order_count = Rice_buy_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                        put_date__year=this_time.year - 1,
                                                        put_date__month=12).count()
            # print('订单情况', this_month_lux_amount, '订单数', order_count, '订单金额', this_month_lux_price)
            this_month_package_money = 0
            for number in range(0, order_count):
                this_month_package_money += this_month_lux_amount[number]['lux_amount'] * \
                                            this_month_lux_price[number]['lux_price']
                # print('计算金额结果', number, '次', this_month_package_money)
            return this_month_package_money
    else:
        return 0


# 进货部分 根据大米比例 计算本月/上月 大包费用统计' 本月/上月'THIS'/'LAST'
def get_in_month_big_money(ratio, package, time):
    if time == 'THIS':
        this_time = datetime.datetime.now()
        this_month_big_amount = Rice_buy_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                              put_date__year=this_time.year,
                                                              put_date__month=this_time.month).values('big_amount')
        this_month_big_price = Rice_buy_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                             put_date__year=this_time.year,
                                                             put_date__month=this_time.month).values('big_price')
        order_count = Rice_buy_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                    put_date__year=this_time.year,
                                                    put_date__month=this_time.month).count()
        # print('订单情况', this_month_big_amount, '订单数', order_count,'订单金额', this_month_big_price)
        this_month_big_money = 0
        for number in range(0, order_count):
            this_month_big_money += this_month_big_amount[number]['big_amount'] * this_month_big_price[number][
                'big_price']
            # print('计算金额结果', number, '次', this_month_big_money)
        return this_month_big_money
    elif time == 'LAST':
        this_time = datetime.datetime.now()
        if this_time.month != 1:
            this_month_big_amount = Rice_buy_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                                  put_date__year=this_time.year,
                                                                  put_date__month=this_time.month - 1).values(
                'big_amount')
            this_month_big_price = Rice_buy_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                                 put_date__year=this_time.year,
                                                                 put_date__month=this_time.month - 1).values(
                'big_price')
            order_count = Rice_buy_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                        put_date__year=this_time.year,
                                                        put_date__month=this_time.month - 1).count()
            # print('订单情况', this_month_big_amount, '订单数', order_count, '订单金额', this_month_big_price)
            this_month_big_money = 0
            for number in range(0, order_count):
                this_month_big_money += this_month_big_amount[number]['big_amount'] * \
                                        this_month_big_price[number]['big_price']
                # print('计算金额结果', number, '次', this_month_big_money)
            return this_month_big_money
        else:
            this_month_big_amount = Rice_buy_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                                  put_date__year=this_time.year - 1,
                                                                  put_date__month=12).values(
                'big_amount')
            this_month_big_price = Rice_buy_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                                 put_date__year=this_time.year - 1,
                                                                 put_date__month=12).values(
                'big_price')
            order_count = Rice_buy_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                        put_date__year=this_time.year - 1,
                                                        put_date__month=12).count()
            # print('订单情况', this_month_big_amount, '订单数', order_count, '订单金额', this_month_big_price)
            this_month_big_money = 0
            for number in range(0, order_count):
                this_month_big_money += this_month_big_amount[number]['big_amount'] * \
                                        this_month_big_price[number]['big_price']
                # print('计算金额结果', number, '次', this_month_big_money)
            return this_month_big_money
    else:
        return 0


# 进货费用 总计 按月 按包装包装参数 'GOLDEN' 'SILVER' 'NORMAL' 本月/上月'THIS'/'LAST'
def get_in_month_total(ratio, package, time):
    return get_in_month_rice_money(ratio, package, time) + get_in_month_package_money(ratio, package,
                                                                                      time) + get_in_month_big_money(
        ratio, package, time)


# 写入进货统计数据
def bought_check():
    Rice_Bought_Check.objects.all().delete()
    new_check_1 = Rice_Bought_Check(check_month='本月', rice_ratio='5:5', package_type='金包装',
                                    rice_money=get_in_month_rice_money('HALF', 'GOLDEN', 'THIS'),
                                    lux_money=get_in_month_package_money('HALF', 'GOLDEN', 'THIS'),
                                    big_money=get_in_month_big_money('HALF', 'GOLDEN', 'THIS'),
                                    total_money=get_in_month_total('HALF', 'GOLDEN', 'THIS'))
    new_check_1.save()
    new_check_2 = Rice_Bought_Check(check_month='本月', rice_ratio='5:5', package_type='银包装',
                                    rice_money=get_in_month_rice_money('HALF', 'SILVER', 'THIS'),
                                    lux_money=get_in_month_package_money('HALF', 'SILVER', 'THIS'),
                                    big_money=get_in_month_big_money('HALF', 'SILVER', 'THIS'),
                                    total_money=get_in_month_total('HALF', 'SILVER', 'THIS'))
    new_check_2.save()
    new_check_3 = Rice_Bought_Check(check_month='本月', rice_ratio='5:5', package_type='牛皮纸',
                                    rice_money=get_in_month_rice_money('HALF', 'NORMAL', 'THIS'),
                                    lux_money=get_in_month_package_money('HALF', 'NORMAL', 'THIS'),
                                    big_money=get_in_month_big_money('HALF', 'NORMAL', 'THIS'),
                                    total_money=get_in_month_total('HALF', 'NORMAL', 'THIS'))
    new_check_3.save()
    new_check_4 = Rice_Bought_Check(check_month='本月', rice_ratio='4:6', package_type='金包装',
                                    rice_money=get_in_month_rice_money('FOUR', 'GOLDEN', 'THIS'),
                                    lux_money=get_in_month_package_money('FOUR', 'GOLDEN', 'THIS'),
                                    big_money=get_in_month_big_money('FOUR', 'GOLDEN', 'THIS'),
                                    total_money=get_in_month_total('FOUR', 'GOLDEN', 'THIS'))
    new_check_4.save()
    new_check_5 = Rice_Bought_Check(check_month='本月', rice_ratio='4:6', package_type='银包装',
                                    rice_money=get_in_month_rice_money('FOUR', 'SILVER', 'THIS'),
                                    lux_money=get_in_month_package_money('FOUR', 'SILVER', 'THIS'),
                                    big_money=get_in_month_big_money('FOUR', 'SILVER', 'THIS'),
                                    total_money=get_in_month_total('FOUR', 'SILVER', 'THIS'))
    new_check_5.save()
    new_check_6 = Rice_Bought_Check(check_month='本月', rice_ratio='4:6', package_type='牛皮纸',
                                    rice_money=get_in_month_rice_money('FOUR', 'NORMAL', 'THIS'),
                                    lux_money=get_in_month_package_money('FOUR', 'NORMAL', 'THIS'),
                                    big_money=get_in_month_big_money('FOUR', 'NORMAL', 'THIS'),
                                    total_money=get_in_month_total('FOUR', 'NORMAL', 'THIS'))
    new_check_6.save()
    new_check_7 = Rice_Bought_Check(check_month='本月', rice_ratio='3:7', package_type='金包装',
                                    rice_money=get_in_month_rice_money('THREE', 'GOLDEN', 'THIS'),
                                    lux_money=get_in_month_package_money('THREE', 'GOLDEN', 'THIS'),
                                    big_money=get_in_month_big_money('THREE', 'GOLDEN', 'THIS'),
                                    total_money=get_in_month_total('THREE', 'GOLDEN', 'THIS'))
    new_check_7.save()
    new_check_8 = Rice_Bought_Check(check_month='本月', rice_ratio='3:7', package_type='银包装',
                                    rice_money=get_in_month_rice_money('THREE', 'SILVER', 'THIS'),
                                    lux_money=get_in_month_package_money('THREE', 'SILVER', 'THIS'),
                                    big_money=get_in_month_big_money('THREE', 'SILVER', 'THIS'),
                                    total_money=get_in_month_total('THREE', 'SILVER', 'THIS'))
    new_check_8.save()
    new_check_9 = Rice_Bought_Check(check_month='本月', rice_ratio='3:7', package_type='牛皮纸',
                                    rice_money=get_in_month_rice_money('THREE', 'NORMAL', 'THIS'),
                                    lux_money=get_in_month_package_money('THREE', 'NORMAL', 'THIS'),
                                    big_money=get_in_month_big_money('THREE', 'NORMAL', 'THIS'),
                                    total_money=get_in_month_total('THREE', 'NORMAL', 'THIS'))
    new_check_9.save()
    new_check_10 = Rice_Bought_Check(check_month='本月合计',
                                     rice_money=get_in_month_rice_money('THREE', 'NORMAL',
                                                                        'THIS') + get_in_month_rice_money('FOUR',
                                                                                                          'NORMAL',
                                                                                                          'THIS') + get_in_month_rice_money(
                                         'HALF', 'NORMAL', 'THIS') + get_in_month_rice_money('THREE', 'SILVER',
                                                                                             'THIS') + get_in_month_rice_money(
                                         'FOUR', 'SILVER', 'THIS') + get_in_month_rice_money('HALF', 'SILVER',
                                                                                             'THIS') + get_in_month_rice_money(
                                         'THREE', 'GOLDEN', 'THIS') + get_in_month_rice_money('FOUR', 'GOLDEN',
                                                                                              'THIS') + get_in_month_rice_money(
                                         'HALF', 'GOLDEN', 'THIS'),
                                     lux_money=get_in_month_package_money('THREE', 'NORMAL',
                                                                          'THIS') + get_in_month_package_money('FOUR',
                                                                                                               'NORMAL',
                                                                                                               'THIS') + get_in_month_package_money(
                                         'HALF', 'NORMAL', 'THIS') + get_in_month_package_money('THREE', 'SILVER',
                                                                                                'THIS') + get_in_month_package_money(
                                         'FOUR', 'SILVER', 'THIS') + get_in_month_package_money('HALF', 'SILVER',
                                                                                                'THIS') + get_in_month_package_money(
                                         'THREE', 'GOLDEN', 'THIS') + get_in_month_package_money('FOUR', 'GOLDEN',
                                                                                                 'THIS') + get_in_month_package_money(
                                         'HALF', 'GOLDEN', 'THIS'),
                                     big_money=get_in_month_big_money('THREE', 'NORMAL',
                                                                      'THIS') + get_in_month_big_money('FOUR', 'NORMAL',
                                                                                                       'THIS') + get_in_month_big_money(
                                         'HALF', 'NORMAL', 'THIS') + get_in_month_big_money('THREE', 'SILVER',
                                                                                            'THIS') + get_in_month_big_money(
                                         'FOUR', 'SILVER', 'THIS') + get_in_month_big_money('HALF', 'SILVER',
                                                                                            'THIS') + get_in_month_big_money(
                                         'THREE', 'GOLDEN', 'THIS') + get_in_month_big_money('FOUR', 'GOLDEN',
                                                                                             'THIS') + get_in_month_big_money(
                                         'HALF', 'GOLDEN', 'THIS'),
                                     total_money=get_in_month_total('THREE', 'NORMAL', 'THIS') + get_in_month_total(
                                         'FOUR', 'NORMAL', 'THIS') + get_in_month_total('HALF', 'NORMAL',
                                                                                        'THIS') + get_in_month_total(
                                         'THREE', 'SILVER', 'THIS') + get_in_month_total('FOUR', 'SILVER',
                                                                                         'THIS') + get_in_month_total(
                                         'HALF', 'SILVER', 'THIS') + get_in_month_total('THREE', 'GOLDEN',
                                                                                        'THIS') + get_in_month_total(
                                         'FOUR', 'GOLDEN', 'THIS') + get_in_month_total('HALF', 'GOLDEN', 'THIS')
                                     )
    new_check_10.save()
    new_check_11 = Rice_Bought_Check(check_month='上月', rice_ratio='5:5', package_type='金包装',
                                     rice_money=get_in_month_rice_money('HALF', 'GOLDEN', 'LAST'),
                                     lux_money=get_in_month_package_money('HALF', 'GOLDEN', 'LAST'),
                                     big_money=get_in_month_big_money('HALF', 'GOLDEN', 'LAST'),
                                     total_money=get_in_month_total('HALF', 'GOLDEN', 'LAST'))
    new_check_11.save()
    new_check_12 = Rice_Bought_Check(check_month='上月', rice_ratio='5:5', package_type='银包装',
                                     rice_money=get_in_month_rice_money('HALF', 'SILVER', 'LAST'),
                                     lux_money=get_in_month_package_money('HALF', 'SILVER', 'LAST'),
                                     big_money=get_in_month_big_money('HALF', 'SILVER', 'LAST'),
                                     total_money=get_in_month_total('HALF', 'SILVER', 'LAST'))
    new_check_12.save()
    new_check_13 = Rice_Bought_Check(check_month='上月', rice_ratio='5:5', package_type='牛皮纸',
                                     rice_money=get_in_month_rice_money('HALF', 'NORMAL', 'LAST'),
                                     lux_money=get_in_month_package_money('HALF', 'NORMAL', 'LAST'),
                                     big_money=get_in_month_big_money('HALF', 'NORMAL', 'LAST'),
                                     total_money=get_in_month_total('HALF', 'NORMAL', 'LAST'))
    new_check_13.save()
    new_check_14 = Rice_Bought_Check(check_month='上月', rice_ratio='4:6', package_type='金包装',
                                     rice_money=get_in_month_rice_money('FOUR', 'GOLDEN', 'LAST'),
                                     lux_money=get_in_month_package_money('FOUR', 'GOLDEN', 'LAST'),
                                     big_money=get_in_month_big_money('FOUR', 'GOLDEN', 'LAST'),
                                     total_money=get_in_month_total('FOUR', 'GOLDEN', 'LAST'))
    new_check_14.save()
    new_check_15 = Rice_Bought_Check(check_month='上月', rice_ratio='4:6', package_type='银包装',
                                     rice_money=get_in_month_rice_money('FOUR', 'SILVER', 'LAST'),
                                     lux_money=get_in_month_package_money('FOUR', 'SILVER', 'LAST'),
                                     big_money=get_in_month_big_money('FOUR', 'SILVER', 'LAST'),
                                     total_money=get_in_month_total('FOUR', 'SILVER', 'LAST'))
    new_check_15.save()
    new_check_16 = Rice_Bought_Check(check_month='上月', rice_ratio='4:6', package_type='牛皮纸',
                                     rice_money=get_in_month_rice_money('FOUR', 'NORMAL', 'LAST'),
                                     lux_money=get_in_month_package_money('FOUR', 'NORMAL', 'LAST'),
                                     big_money=get_in_month_big_money('FOUR', 'NORMAL', 'LAST'),
                                     total_money=get_in_month_total('FOUR', 'NORMAL', 'LAST'))
    new_check_16.save()
    new_check_17 = Rice_Bought_Check(check_month='上月', rice_ratio='3:7', package_type='金包装',
                                     rice_money=get_in_month_rice_money('THREE', 'GOLDEN', 'LAST'),
                                     lux_money=get_in_month_package_money('THREE', 'GOLDEN', 'LAST'),
                                     big_money=get_in_month_big_money('THREE', 'GOLDEN', 'LAST'),
                                     total_money=get_in_month_total('THREE', 'GOLDEN', 'LAST'))
    new_check_17.save()
    new_check_18 = Rice_Bought_Check(check_month='上月', rice_ratio='3:7', package_type='银包装',
                                     rice_money=get_in_month_rice_money('THREE', 'SILVER', 'LAST'),
                                     lux_money=get_in_month_package_money('THREE', 'SILVER', 'LAST'),
                                     big_money=get_in_month_big_money('THREE', 'SILVER', 'LAST'),
                                     total_money=get_in_month_total('THREE', 'SILVER', 'LAST'))
    new_check_18.save()
    new_check_19 = Rice_Bought_Check(check_month='上月', rice_ratio='3:7', package_type='牛皮纸',
                                     rice_money=get_in_month_rice_money('THREE', 'NORMAL', 'LAST'),
                                     lux_money=get_in_month_package_money('THREE', 'NORMAL', 'LAST'),
                                     big_money=get_in_month_big_money('THREE', 'NORMAL', 'LAST'),
                                     total_money=get_in_month_total('THREE', 'NORMAL', 'LAST'))
    new_check_19.save()
    new_check_20 = Rice_Bought_Check(check_month='上月合计',
                                     rice_money=get_in_month_rice_money('THREE', 'NORMAL',
                                                                        'LAST') + get_in_month_rice_money('FOUR',
                                                                                                          'NORMAL',
                                                                                                          'LAST') + get_in_month_rice_money(
                                         'HALF', 'NORMAL', 'LAST') + get_in_month_rice_money('THREE', 'SILVER',
                                                                                             'LAST') + get_in_month_rice_money(
                                         'FOUR', 'SILVER', 'LAST') + get_in_month_rice_money('HALF', 'SILVER',
                                                                                             'LAST') + get_in_month_rice_money(
                                         'THREE', 'GOLDEN', 'LAST') + get_in_month_rice_money('FOUR', 'GOLDEN',
                                                                                              'LAST') + get_in_month_rice_money(
                                         'HALF', 'GOLDEN', 'LAST'),
                                     lux_money=get_in_month_package_money('THREE', 'NORMAL',
                                                                          'LAST') + get_in_month_package_money('FOUR',
                                                                                                               'NORMAL',
                                                                                                               'LAST') + get_in_month_package_money(
                                         'HALF', 'NORMAL', 'LAST') + get_in_month_package_money('THREE', 'SILVER',
                                                                                                'LAST') + get_in_month_package_money(
                                         'FOUR', 'SILVER', 'LAST') + get_in_month_package_money('HALF', 'SILVER',
                                                                                                'LAST') + get_in_month_package_money(
                                         'THREE', 'GOLDEN', 'LAST') + get_in_month_package_money('FOUR', 'GOLDEN',
                                                                                                 'LAST') + get_in_month_package_money(
                                         'HALF', 'GOLDEN', 'LAST'),
                                     big_money=get_in_month_big_money('THREE', 'NORMAL',
                                                                      'LAST') + get_in_month_big_money('FOUR', 'NORMAL',
                                                                                                       'LAST') + get_in_month_big_money(
                                         'HALF', 'NORMAL', 'LAST') + get_in_month_big_money('THREE', 'SILVER',
                                                                                            'LAST') + get_in_month_big_money(
                                         'FOUR', 'SILVER', 'LAST') + get_in_month_big_money('HALF', 'SILVER',
                                                                                            'LAST') + get_in_month_big_money(
                                         'THREE', 'GOLDEN', 'LAST') + get_in_month_big_money('FOUR', 'GOLDEN',
                                                                                             'LAST') + get_in_month_big_money(
                                         'HALF', 'GOLDEN', 'LAST'),
                                     total_money=get_in_month_total('THREE', 'NORMAL', 'LAST') + get_in_month_total(
                                         'FOUR', 'NORMAL', 'LAST') + get_in_month_total('HALF', 'NORMAL',
                                                                                        'LAST') + get_in_month_total(
                                         'THREE', 'SILVER', 'LAST') + get_in_month_total('FOUR', 'SILVER',
                                                                                         'LAST') + get_in_month_total(
                                         'HALF', 'SILVER', 'LAST') + get_in_month_total('THREE', 'GOLDEN',
                                                                                        'LAST') + get_in_month_total(
                                         'FOUR', 'GOLDEN', 'LAST') + get_in_month_total('HALF', 'GOLDEN', 'LAST')
                                     )
    new_check_20.save()


# 销售统计数据 大米金额
def sell_out_month_rice_money(ratio, package, time):
    if time == 'THIS':
        this_time = datetime.datetime.now()
        this_month_order_amount = Rice_sell_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                                 put_date__year=this_time.year,
                                                                 put_date__month=this_time.month).values('order_amount')
        this_month_order_price = Rice_sell_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                                put_date__year=this_time.year,
                                                                put_date__month=this_time.month).values('order_price')
        order_count = Rice_sell_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                     put_date__year=this_time.year,
                                                     put_date__month=this_time.month).count()
        # print('订单情况', this_month_order_amount, '订单数', order_count,'订单金额', this_month_order_price)
        this_month_rice_money = 0
        for number in range(0, order_count):
            this_month_rice_money += this_month_order_amount[number]['order_amount'] * this_month_order_price[number][
                'order_price']
            # print('计算金额结果', number, '次', this_month_rice_money)
        return this_month_rice_money
    elif time == 'LAST':
        this_time = datetime.datetime.now()
        if this_time.month != 1:
            this_month_order_amount = Rice_sell_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                                     put_date__year=this_time.year,
                                                                     put_date__month=this_time.month - 1).values(
                'order_amount')
            this_month_order_price = Rice_sell_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                                    put_date__year=this_time.year,
                                                                    put_date__month=this_time.month - 1).values(
                'order_price')
            order_count = Rice_sell_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                         put_date__year=this_time.year,
                                                         put_date__month=this_time.month - 1).count()
            # print('订单情况', this_month_order_amount, '订单数', order_count, '订单金额', this_month_order_price)
            this_month_rice_money = 0
            for number in range(0, order_count):
                this_month_rice_money += this_month_order_amount[number]['order_amount'] * \
                                         this_month_order_price[number]['order_price']
                # print('计算金额结果', number, '次', this_month_rice_money)
            return this_month_rice_money
        else:
            this_month_order_amount = Rice_sell_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                                     put_date__year=this_time.year - 1,
                                                                     put_date__month=12).values(
                'order_amount')
            this_month_order_price = Rice_sell_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                                    put_date__year=this_time.year - 1,
                                                                    put_date__month=12).values(
                'order_price')
            order_count = Rice_sell_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                         put_date__year=this_time.year - 1,
                                                         put_date__month=12).count()
            # print('订单情况', this_month_order_amount, '订单数', order_count, '订单金额', this_month_order_price)
            this_month_rice_money = 0
            for number in range(0, order_count):
                this_month_rice_money += this_month_order_amount[number]['order_amount'] * \
                                         this_month_order_price[number]['order_price']
                # print('计算金额结果', number, '次', this_month_rice_money)
            return this_month_rice_money
    else:
        return 0


# 销售运费统计
def sell_delivery_month_rice_money(ratio, package, time):
    if time == 'THIS':
        this_time = datetime.datetime.now()
        this_month_order_amount = Rice_sell_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                                 put_date__year=this_time.year,
                                                                 put_date__month=this_time.month).values('order_amount')
        this_month_delivery_fee = Rice_sell_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                                 put_date__year=this_time.year,
                                                                 put_date__month=this_time.month).values('delivery_fee')
        order_count = Rice_sell_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                     put_date__year=this_time.year,
                                                     put_date__month=this_time.month).count()
        # print('订单情况', this_month_order_amount, '订单数', order_count,'订单金额', this_month_delivery_fee)
        this_month_rice_money = 0
        for number in range(0, order_count):
            this_month_rice_money += this_month_order_amount[number]['order_amount'] * this_month_delivery_fee[number][
                'delivery_fee']
            # print('计算金额结果', number, '次', this_month_rice_money)
        return this_month_rice_money
    elif time == 'LAST':
        this_time = datetime.datetime.now()
        if this_time.month != 1:
            this_month_order_amount = Rice_sell_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                                     put_date__year=this_time.year,
                                                                     put_date__month=this_time.month - 1).values(
                'order_amount')
            this_month_delivery_fee = Rice_sell_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                                     put_date__year=this_time.year,
                                                                     put_date__month=this_time.month - 1).values(
                'delivery_fee')
            order_count = Rice_sell_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                         put_date__year=this_time.year,
                                                         put_date__month=this_time.month - 1).count()
            # print('订单情况', this_month_order_amount, '订单数', order_count, '订单金额', this_month_delivery_fee)
            this_month_rice_money = 0
            for number in range(0, order_count):
                this_month_rice_money += this_month_order_amount[number]['order_amount'] * \
                                         this_month_delivery_fee[number]['delivery_fee']
                # print('计算金额结果', number, '次', this_month_rice_money)
            return this_month_rice_money
        else:
            this_month_order_amount = Rice_sell_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                                     put_date__year=this_time.year - 1,
                                                                     put_date__month=12).values(
                'order_amount')
            this_month_delivery_fee = Rice_sell_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                                     put_date__year=this_time.year - 1,
                                                                     put_date__month=12).values(
                'delivery_fee')
            order_count = Rice_sell_order.objects.filter(get_package=package, get_rice_ratio=ratio,
                                                         put_date__year=this_time.year - 1,
                                                         put_date__month=12).count()
            # print('订单情况', this_month_order_amount, '订单数', order_count, '订单金额', this_month_delivery_fee)
            this_month_rice_money = 0
            for number in range(0, order_count):
                this_month_rice_money += this_month_order_amount[number]['order_amount'] * \
                                         this_month_delivery_fee[number]['delivery_fee']
                # print('计算金额结果', number, '次', this_month_rice_money)
            return this_month_rice_money
    else:
        return 0


def sell_total_month(ratio, package, time):
    return sell_out_month_rice_money(ratio, package, time) + sell_delivery_month_rice_money(ratio, package, time)


def sell_check():
    Rice_Sell_Check.objects.all().delete()
    new_check_1 = Rice_Sell_Check(check_month='本月', rice_ratio='5:5', package_type='金包装',
                                  rice_money=sell_out_month_rice_money('HALF', 'GOLDEN', 'THIS'),
                                  delivery_money=sell_delivery_month_rice_money('HALF', 'GOLDEN', 'THIS'),
                                  total_money=sell_total_month('HALF', 'GOLDEN', 'THIS'))
    new_check_1.save()
    new_check_2 = Rice_Sell_Check(check_month='本月', rice_ratio='5:5', package_type='银包装',
                                  rice_money=sell_out_month_rice_money('HALF', 'SILVER', 'THIS'),
                                  delivery_money=sell_delivery_month_rice_money('HALF', 'SILVER', 'THIS'),
                                  total_money=sell_total_month('HALF', 'SILVER', 'THIS'))
    new_check_2.save()
    new_check_3 = Rice_Sell_Check(check_month='本月', rice_ratio='5:5', package_type='牛皮纸',
                                  rice_money=sell_out_month_rice_money('HALF', 'NORMAL', 'THIS'),
                                  delivery_money=sell_delivery_month_rice_money('HALF', 'NORMAL', 'THIS'),
                                  total_money=sell_total_month('HALF', 'NORMAL', 'THIS'))
    new_check_3.save()
    new_check_4 = Rice_Sell_Check(check_month='本月', rice_ratio='4:6', package_type='金包装',
                                  rice_money=sell_out_month_rice_money('FOUR', 'GOLDEN', 'THIS'),
                                  delivery_money=sell_delivery_month_rice_money('FOUR', 'GOLDEN', 'THIS'),
                                  total_money=sell_total_month('FOUR', 'GOLDEN', 'THIS'))
    new_check_4.save()
    new_check_5 = Rice_Sell_Check(check_month='本月', rice_ratio='4:6', package_type='银包装',
                                  rice_money=sell_out_month_rice_money('FOUR', 'SILVER', 'THIS'),
                                  delivery_money=sell_delivery_month_rice_money('FOUR', 'SILVER', 'THIS'),
                                  total_money=sell_total_month('FOUR', 'SILVER', 'THIS'))
    new_check_5.save()
    new_check_6 = Rice_Sell_Check(check_month='本月', rice_ratio='4:6', package_type='牛皮纸',
                                  rice_money=sell_out_month_rice_money('FOUR', 'NORMAL', 'THIS'),
                                  delivery_money=sell_delivery_month_rice_money('FOUR', 'NORMAL', 'THIS'),
                                  total_money=sell_total_month('FOUR', 'NORMAL', 'THIS'))
    new_check_6.save()
    new_check_7 = Rice_Sell_Check(check_month='本月', rice_ratio='3:7', package_type='金包装',
                                  rice_money=sell_out_month_rice_money('THREE', 'GOLDEN', 'THIS'),
                                  delivery_money=sell_delivery_month_rice_money('THREE', 'GOLDEN', 'THIS'),
                                  total_money=sell_total_month('THREE', 'GOLDEN', 'THIS'))
    new_check_7.save()
    new_check_8 = Rice_Sell_Check(check_month='本月', rice_ratio='3:7', package_type='银包装',
                                  rice_money=sell_out_month_rice_money('THREE', 'SILVER', 'THIS'),
                                  delivery_money=sell_delivery_month_rice_money('THREE', 'SILVER', 'THIS'),
                                  total_money=sell_total_month('THREE', 'SILVER', 'THIS'))
    new_check_8.save()
    new_check_9 = Rice_Sell_Check(check_month='本月', rice_ratio='3:7', package_type='牛皮纸',
                                  rice_money=sell_out_month_rice_money('THREE', 'NORMAL', 'THIS'),
                                  delivery_money=sell_delivery_month_rice_money('THREE', 'NORMAL', 'THIS'),
                                  total_money=sell_total_month('THREE', 'NORMAL', 'THIS'))
    new_check_9.save()
    new_check_10 = Rice_Sell_Check(check_month='本月合计',
                                   rice_money=sell_out_month_rice_money('THREE', 'NORMAL',
                                                                        'THIS') + sell_out_month_rice_money('FOUR',
                                                                                                            'NORMAL',
                                                                                                            'THIS') + sell_out_month_rice_money(
                                       'HALF', 'NORMAL', 'THIS') + sell_out_month_rice_money('THREE', 'SILVER',
                                                                                             'THIS') + sell_out_month_rice_money(
                                       'FOUR', 'SILVER', 'THIS') + sell_out_month_rice_money('HALF', 'SILVER',
                                                                                             'THIS') + sell_out_month_rice_money(
                                       'THREE', 'GOLDEN', 'THIS') + sell_out_month_rice_money('FOUR', 'GOLDEN',
                                                                                              'THIS') + sell_out_month_rice_money(
                                       'HALF', 'GOLDEN', 'THIS'),
                                   delivery_money=sell_delivery_month_rice_money('THREE', 'NORMAL',
                                                                                 'THIS') + sell_delivery_month_rice_money(
                                       'FOUR', 'NORMAL', 'THIS') + sell_delivery_month_rice_money('HALF', 'NORMAL',
                                                                                                  'THIS') + sell_delivery_month_rice_money(
                                       'THREE', 'SILVER', 'THIS') + sell_delivery_month_rice_money('FOUR', 'SILVER',
                                                                                                   'THIS') + sell_delivery_month_rice_money(
                                       'HALF', 'SILVER', 'THIS') + sell_delivery_month_rice_money('THREE', 'GOLDEN',
                                                                                                  'THIS') + sell_delivery_month_rice_money(
                                       'FOUR', 'GOLDEN', 'THIS') + sell_delivery_month_rice_money('HALF', 'GOLDEN',
                                                                                                  'THIS'),
                                   total_money=sell_total_month('THREE', 'NORMAL', 'THIS') + sell_total_month('FOUR',
                                                                                                              'NORMAL',
                                                                                                              'THIS') + sell_total_month(
                                       'HALF', 'NORMAL', 'THIS') + sell_total_month('THREE', 'SILVER',
                                                                                    'THIS') + sell_total_month('FOUR',
                                                                                                               'SILVER',
                                                                                                               'THIS') + sell_total_month(
                                       'HALF', 'SILVER', 'THIS') + sell_total_month('THREE', 'GOLDEN',
                                                                                    'THIS') + sell_total_month('FOUR',
                                                                                                               'GOLDEN',
                                                                                                               'THIS') + sell_total_month(
                                       'HALF', 'GOLDEN', 'THIS')
                                   )
    new_check_10.save()
    new_check_11 = Rice_Sell_Check(check_month='上月', rice_ratio='5:5', package_type='金包装',
                                   rice_money=sell_out_month_rice_money('HALF', 'GOLDEN', 'LAST'),
                                   delivery_money=sell_delivery_month_rice_money('HALF', 'GOLDEN', 'LAST'),
                                   total_money=sell_total_month('HALF', 'GOLDEN', 'LAST'))
    new_check_11.save()
    new_check_12 = Rice_Sell_Check(check_month='上月', rice_ratio='5:5', package_type='银包装',
                                   rice_money=sell_out_month_rice_money('HALF', 'SILVER', 'LAST'),
                                   delivery_money=sell_delivery_month_rice_money('HALF', 'SILVER', 'LAST'),
                                   total_money=sell_total_month('HALF', 'SILVER', 'LAST'))
    new_check_12.save()
    new_check_13 = Rice_Sell_Check(check_month='上月', rice_ratio='5:5', package_type='牛皮纸',
                                   rice_money=sell_out_month_rice_money('HALF', 'NORMAL', 'LAST'),
                                   delivery_money=sell_delivery_month_rice_money('HALF', 'NORMAL', 'LAST'),
                                   total_money=sell_total_month('HALF', 'NORMAL', 'LAST'))
    new_check_13.save()
    new_check_14 = Rice_Sell_Check(check_month='上月', rice_ratio='4:6', package_type='金包装',
                                   rice_money=sell_out_month_rice_money('FOUR', 'GOLDEN', 'LAST'),
                                   delivery_money=sell_delivery_month_rice_money('FOUR', 'GOLDEN', 'LAST'),
                                   total_money=sell_total_month('FOUR', 'GOLDEN', 'LAST'))
    new_check_14.save()
    new_check_15 = Rice_Sell_Check(check_month='上月', rice_ratio='4:6', package_type='银包装',
                                   rice_money=sell_out_month_rice_money('FOUR', 'SILVER', 'LAST'),
                                   delivery_money=sell_delivery_month_rice_money('FOUR', 'SILVER', 'LAST'),
                                   total_money=sell_total_month('FOUR', 'SILVER', 'LAST'))
    new_check_15.save()
    new_check_16 = Rice_Sell_Check(check_month='上月', rice_ratio='4:6', package_type='牛皮纸',
                                   rice_money=sell_out_month_rice_money('FOUR', 'NORMAL', 'LAST'),
                                   delivery_money=sell_delivery_month_rice_money('FOUR', 'NORMAL', 'LAST'),
                                   total_money=sell_total_month('FOUR', 'NORMAL', 'LAST'))
    new_check_16.save()
    new_check_17 = Rice_Sell_Check(check_month='上月', rice_ratio='3:7', package_type='金包装',
                                   rice_money=sell_out_month_rice_money('THREE', 'GOLDEN', 'LAST'),
                                   delivery_money=sell_delivery_month_rice_money('THREE', 'GOLDEN', 'LAST'),
                                   total_money=sell_total_month('THREE', 'GOLDEN', 'LAST'))
    new_check_17.save()
    new_check_18 = Rice_Sell_Check(check_month='上月', rice_ratio='3:7', package_type='银包装',
                                   rice_money=sell_out_month_rice_money('THREE', 'SILVER', 'LAST'),
                                   delivery_money=sell_delivery_month_rice_money('THREE', 'SILVER', 'LAST'),
                                   total_money=sell_total_month('THREE', 'SILVER', 'LAST'))
    new_check_18.save()
    new_check_19 = Rice_Sell_Check(check_month='上月', rice_ratio='3:7', package_type='牛皮纸',
                                   rice_money=sell_out_month_rice_money('THREE', 'NORMAL', 'LAST'),
                                   delivery_money=sell_delivery_month_rice_money('THREE', 'NORMAL', 'LAST'),
                                   total_money=sell_total_month('THREE', 'NORMAL', 'LAST'))
    new_check_19.save()
    new_check_20 = Rice_Sell_Check(check_month='上月合计',
                                   rice_money=sell_out_month_rice_money('THREE', 'NORMAL',
                                                                        'LAST') + sell_out_month_rice_money('FOUR',
                                                                                                            'NORMAL',
                                                                                                            'LAST') + sell_out_month_rice_money(
                                       'HALF', 'NORMAL', 'LAST') + sell_out_month_rice_money('THREE', 'SILVER',
                                                                                             'LAST') + sell_out_month_rice_money(
                                       'FOUR', 'SILVER', 'LAST') + sell_out_month_rice_money('HALF', 'SILVER',
                                                                                             'LAST') + sell_out_month_rice_money(
                                       'THREE', 'GOLDEN', 'LAST') + sell_out_month_rice_money('FOUR', 'GOLDEN',
                                                                                              'LAST') + sell_out_month_rice_money(
                                       'HALF', 'GOLDEN', 'LAST'),
                                   delivery_money=sell_delivery_month_rice_money('THREE', 'NORMAL',
                                                                                 'LAST') + sell_delivery_month_rice_money(
                                       'FOUR', 'NORMAL', 'LAST') + sell_delivery_month_rice_money('HALF', 'NORMAL',
                                                                                                  'LAST') + sell_delivery_month_rice_money(
                                       'THREE', 'SILVER', 'LAST') + sell_delivery_month_rice_money('FOUR', 'SILVER',
                                                                                                   'LAST') + sell_delivery_month_rice_money(
                                       'HALF', 'SILVER', 'LAST') + sell_delivery_month_rice_money('THREE', 'GOLDEN',
                                                                                                  'LAST') + sell_delivery_month_rice_money(
                                       'FOUR', 'GOLDEN', 'LAST') + sell_delivery_month_rice_money('HALF', 'GOLDEN',
                                                                                                  'LAST'),
                                   total_money=sell_total_month('THREE', 'NORMAL', 'LAST') + sell_total_month('FOUR',
                                                                                                              'NORMAL',
                                                                                                              'LAST') + sell_total_month(
                                       'HALF', 'NORMAL', 'LAST') + sell_total_month('THREE', 'SILVER',
                                                                                    'LAST') + sell_total_month('FOUR',
                                                                                                               'SILVER',
                                                                                                               'LAST') + sell_total_month(
                                       'HALF', 'SILVER', 'LAST') + sell_total_month('THREE', 'GOLDEN',
                                                                                    'LAST') + sell_total_month('FOUR',
                                                                                                               'GOLDEN',
                                                                                                               'LAST') + sell_total_month(
                                       'HALF', 'GOLDEN', 'LAST')
                                   )
    new_check_20.save()


class Rice_Bought_Check_Admin(admin.ModelAdmin):
    list_display = ['id', 'check_month', 'rice_ratio', 'package_type', 'rice_money', 'lux_money', 'big_money',
                    'total_money']
    list_display_links = ['check_month']
    list_per_page = 20
    ordering = ['id']

    # change_list_template = 'admin/change_list.html'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Rice_Bought_Check, Rice_Bought_Check_Admin)


class Rice_Sell_Check_Admin(admin.ModelAdmin):
    list_display = ['check_month', 'rice_ratio', 'package_type', 'rice_money', 'delivery_money', 'total_money']
    list_display_links = ['check_month']
    list_per_page = 20
    ordering = ['id']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Rice_Sell_Check, Rice_Sell_Check_Admin)


# 定时生成报表
def task():
    bought_check()
    stock_check_admin()
    sell_check()


# 载入/刷新页面时候 加载 bought_check() stock_check_admin() sell_check()看看能不能绑定刷新按钮上
# 表格宽度调整 颜色调整
# 软删除改为真删除

num_test = 0


def print_test():
    print(num_test)
    num_test += 1
