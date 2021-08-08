# fsastdfs测试
from fdfs_client.client import Fdfs_client
client = Fdfs_client('utils/FastDFS/client.conf')

client.upload_by_filename(r"/mnt/d/asus/Pictures/Saved Pictures/wallhaven-dp3yg3.jpg")