import typing

from ..handler import DBHandler, ESHandler, ClientHandler
from ..utils import db_params, get_info_from_environ

class BaseClient:

    def __init__(self, client, **options):
        self._client = client
        self.handler: ClientHandler = self.handler_class(self.hosts, **options)

    @property
    def ip(self):
        return self._client.ip

    @property
    def client(self):
        return self._client

    @property
    def hosts(self):
        pass

    def _from_env(self):
        cli_prefix = self.__client_prefix__
        try:
            import os
            info = get_info_from_environ(os.environ,
                                         lambda K: K.startswith(cli_prefix))
        except Exception:
            info = None
        return info

class DBClient(BaseClient):

    __client_prefix__ = 'DB'
    handler_class = DBHandler

    @property
    def hosts(self):
        info = self._from_env()
        if 'db_ip' not in info:
            if not self.ip:
                raise EnvironmentError('Ip must be in environment variables')
            info.update({'db_ip': self.ip})
        url = self._make_url(info)
        return url

    def _make_url(self, info):
        url = self._url_form()
        for key, value in info.items():
            url = url.replace(key, value)
        return url

    def _url_form(self):
        return 'mysql+pymysql://db_user:db_pwd@db_ip/db_name'

    @db_params(model='User')
    def user(self,
             action: str,
             model: 'MODEL',
             mapping: typing.Dict[str, typing.Any],
             relations: typing.Optional[typing.Dict[str, typing.Any]] = None,
             response_model: typing.Optional['SCHEMA'] = None,
             filter=None,
             order_by=None,
             **kwargs):

        return self.handler.perform(action,
                                    model=model,
                                    mapping=mapping,
                                    relations=relations,
                                    response_model=response_model,
                                    filter=filter,
                                    order_by=order_by,
                                    **kwargs)

    @db_params(model='Project')
    def project(self,
                action: str,
                model: 'MODEL',
                mapping: typing.Dict[str, typing.Any],
                relations: typing.Optional[typing.Dict[str, typing.Any]] = None,
                response_model: typing.Optional['SCHEMA'] = None,
                filter=None,
                order_by=None,
                **kwargs):
        # find는 불가

        return self.handler.perform(action,
                                    model=model,
                                    mapping=mapping,
                                    relations=relations,
                                    response_model=response_model,
                                    filter=filter,
                                    order_by=order_by,
                                    **kwargs)

    @db_params(model='ProjectUser') # ismine 옵션 적용시
    def find_project_per_user(self,
                              action,
                              model,
                              mapping,
                              relations,
                              response_model=None,
                              filter=None,
                              order_by=None,
                              **kwargs):
        return self.handler.perform(action,
                                    model=model,
                                    mapping=mapping,
                                    relations=relations,
                                    response_model=response_model,
                                    filter=filter,
                                    order_by=order_by,
                                    **kwargs)



    @db_params(model='User',
               fields=['user_id', 'user'])
    def create_user(self, action, model, mapping,
                    relations=None, response_model=None, filter=None, order_by=None, **kwargs):
        return self.handler.perform(action,
                                    model=model,
                                    mapping=mapping,
                                    relations=relations,
                                    response_model=response_model,
                                    filter=filter,
                                    order_by=order_by,
                                    **kwargs)

    @db_params(model='Cartegory')
    def category(self, action, model, mapping,
                  relations=None, response_model=None, filter=None, order_by=None, **kwargs):

        return self.handler.perform(action,
                                    model=model,
                                    mapping=mapping,
                                    relations=relations,
                                    response_model=response_model,
                                    filter=filter,
                                    order_by=order_by,
                                    **kwargs)

    @db_params(model='Origin')
    def origin(self, action, model, mapping,
                relations=None, response_model=None, filter=None, order_by=None, **kwargs):
        #origin 생성시 반드시 synnoym도 같이 들어와야한다
        return self.handler.perform(action,
                                    model=model,
                                    mapping=mapping,
                                    relations=relations,
                                    response_model=response_model,
                                    filter=filter,
                                    order_by=order_by,
                                    **kwargs)

    @db_params(model='Synonym')
    def synonym(self, action, model, mapping,
               relations=None, response_model=None, filter=None, order_by=None, **kwargs):
        # origin 생성시 반드시 synnoym도 같이 들어와야한다
        return self.handler.perform(action,
                                    model=model,
                                    mapping=mapping,
                                    relations=relations,
                                    response_model=response_model,
                                    filter=filter,
                                    order_by=order_by,
                                    **kwargs)

    # (field, operator(연산자 조합)
    # and, or는 순서 지켜서 쓰자 아니면.....
    # relation 경우 어떻게 처리할지 로직을 추가해야 할 수도..
    # ordering 이 한 테이블로 어려울 경우 reponse model에 메소드(class method)를 추가해서 하자

class ElasticsearchClient(BaseClient):
    __client_prefix__ = 'ES'
    handler_class = ESHandler

    @property
    def hosts(self):
        pass


