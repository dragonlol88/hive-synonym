# 통합 client 정의
# query, pth parameter는 메소드에 정의 하기??????????????

import typing
from .client import DBClient
from .client import ElasticsearchClient


class Synonyms:

    def __init__(self,
                 ip=None,
                 port=None,
                 **options):
        self.ip = ip
        self.port = port
        self.options = options
        self.__es = ElasticsearchClient
        self.__db = DBClient


    @property
    def db(self):
        # 런타임 호출시 연결
        options = self.options
        return self.__db(self, **options)

    @property
    def es(self):
        #런타임 호출시 연결
        options = self.options
        return self.__es(self, options)

    def synonyms(self, q):
        es = self.es