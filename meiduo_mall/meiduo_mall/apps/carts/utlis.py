import pickle
import base64
from django_redis import get_redis_connection
def get_carts(request,response,user):
    # 合並購物車
    # 獲取cookie 數據
    cart_cookie=request.COOKIES.get('cart_cookie')
    if not cart_cookie:
        return response

    data_dict=pickle.loads(base64.b64decode(cart_cookie))

    if data_dict is None:
        return response
    cart_dict={}
    cart_list=[]
    cart_list_none=[]
    for sku_id,sku_data in data_dict.items():
        cart_dict[sku_id] = sku_data['count']
        if sku_data['selected']:
            cart_list.append(sku_id)
        else:
            cart_list_none.append(sku_id)

    # 寫入redis
    client=get_redis_connection('carts')
    client.hmet('carts_%s'%user.id,cart_dict)

    if cart_list:
        client.sadd('carts_selected_%d'%user.id,*cart_list)
    if cart_list_none:
        client.srem('carts_selected_%d'%user.id,*cart_list_none)
    response.delete_cookie('cart_cookie')
    return  response