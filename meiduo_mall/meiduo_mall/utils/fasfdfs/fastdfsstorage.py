from django.core.files.storage import Storage


class FastDFSStorage(Storage):
    def _oepn(self):
        pass

    def _save(self):
        pass

    def url(self, name):
        """
            拼接图片路径
        :param name: 数据中存储的路径
        :return:
        """

        return 'http://192.168.18.36:8888/' + name
