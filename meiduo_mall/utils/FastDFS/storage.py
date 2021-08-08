from django.core.files.storage import Storage
from django.conf import settings


class FastDFSStorage(Storage):
    """
    自定义文件存储中的url方法，实现ImageFiled的图片.url方法，添加fsatdfs的地址前缀
    """
    # 详见https://docs.djangoproject.com/en/2.2/howto/custom-file-storage/
    def __init__(self, fdfs_base_url=None):
        self.fdfs_base_url = fdfs_base_url or settings.FDFS_BASE_URL

    def _open(self, name, mode='rb'):
        """Retrieve the specified file from storage."""
        # 打开文件时使用的，此时不需要，而文档告诉说明必须实现，所以pass
        pass

    def _save(self, name, content):
        # 保存文件时使用的，此时不需要，而文档告诉说明必须实现，所以pass
        pass

    def url(self, name):
        """
        返回name所指文件的绝对URL
        """
        #
        return self.fdfs_base_url + name
