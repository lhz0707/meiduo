from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User
from datetime import date, timedelta
from rest_framework.permissions import IsAdminUser
from goods.models import GoodsVisitCount
class UserTotalCount(APIView):
    # 权限指定
    permission_classes = [IsAdminUser]
    def get(self,request):
        # 获取用户总数
# 查询用户表中的数据
        count=User.objects.filter(is_staff=False).count()

        return  Response({
            'count':count,
            'date':date.today()
        })


# 日增用户的获取
class UserDayCount(APIView):
    permission_classes = [IsAdminUser]

    def get(self,request):

        # 获取日增用户

# 获取当前日期
        now_date=date.today()

        # 查询注册用户
        count=User.objects.filter(date_joined__gte=now_date,is_staff=False).count()
        return  Response({
            'count':count,
            'date':now_date
        })


class UserDayActiveCount(APIView):
    permission_classes = [IsAdminUser]

    def get(self,request):
        # 获取日活用户
        # 当天日期
        now_date=date.today()

        # 查询用户
        count=User.objects.filter(last_login__gte=now_date,is_staff=False).count()

        return Response({
            'count':count,
            'date':now_date
        })

#获取下单用户
class UserDayOrdersCount(APIView):
    permission_classes = [IsAdminUser]

    def get(self,request):

        # 当天日期
        now_date=date.today()

        # 查询下单
        users=set(User.objects.filter(orderinfo__create_time__gte=now_date,is_staff=False))

        count=len(users)
        return Response({
            'count':count,
            'date':now_date
        })


class  UserMonthCount(APIView):
    permission_classes = [IsAdminUser]
    def get(self,request):

        # 获取月曾用户
        now_date=date.today()

        # 获取30天的时间
        old_date=now_date -timedelta(days=30)

        # 遍历30天范围内注册用户数量 每编列
        date_list=[]

        for i in range(31):
            # 获取当前日期
            index_date =old_date+timedelta(i)

            # 获取下一天日期
            next_date=old_date+timedelta(i+1)

            count=User.objects.filter(date_joined__gte=index_date,date_joined__lt=next_date,is_staff=False).count()

            date_list.append({
                'count':count,
                'date':index_date
            })

            return  Response(date_list)

class GoodsTypeCount(APIView):
    permission_classes = [IsAdminUser]
    def get(self,request):
        # 获取商品分类访问
        # 获取当天时间
        now_date=date.today()

        # 查询商品分类表
        goodscount=GoodsVisitCount.objects.filter(date=now_date)

        # 获取数量
        data_list=[]
        for goods in goodscount:
            data_list.append({
                'count':goods.count,
                'category':goods.category.name
            })

        return Response(data_list)