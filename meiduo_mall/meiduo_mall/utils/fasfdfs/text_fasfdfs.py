from fdfs_client.client import Fdfs_client

client = Fdfs_client('./client.conf')
with open('client.conf', 'rb') as f:
    data = f.read()

# res=client.upload_by_filename('client.conf')
# 上传文件的二进制数据
res = client.upload_by_buffer(data)

print(res)
