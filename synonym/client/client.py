import typing
from ..handler import DBHandler, ESHandler, ClientHandler
from ..utils import db_params


class BaseClient:

    def __init__(self, client, **options):
        self._client = client
        self.handler: ClientHandler = self.handler_class(self.hosts, **options)

    @property
    def client(self):
        return self._client

    @property
    def hosts(self):
        pass


class DBClient(BaseClient):
    handler_class = DBHandler

    @property
    def hosts(self):
        ip = self.client.ip
        port = self.client.port
        pwd = 'chldydtjs1#'
        user_id = 'sunny'
        dev = 'es-synonym'
        url = f'mysql+pymysql://{user_id}:{pwd}@{ip}/{dev}'
        return url

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

    @db_params(model='Origin',
               order_by={'id': 'desc'})
    def find_origin(self,
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

    @db_params(model='Project',
               where=[('id', 'on_off')],
               set=['pjt_name'])
    def update_project(self,
                    action: str,
                    model: 'MODEL',
                    mapping: typing.Dict[str, typing.Any],
                    relations: typing.Optional[typing.Dict[str, typing.Any]] = None,
                    response_model: typing.Optional['SCHEMA'] = None,
                    filter=None,
                    **kwargs):
        return self.handler.perform(action,
                                    model=model,
                                    mapping=mapping,
                                    relations=relations,
                                    response_model=response_model,
                                    filter=filter,
                                    **kwargs)


class ElasticsearchClient(BaseClient):
    handler_class = ESHandler

    @property
    def hosts(self):
        pass


