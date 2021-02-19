from flask import Flask
from synonym.apps.api import create_synonyms_rest_app
from synonym.client import Synonyms
from synonym.response import ProjectResponse, OriginResponse, ProjectUserResponse
from synonym.response import project_find_post_process, CategoryResponse, OriginResponse, SynonymResponse , update_pre_process
import typing
syn = Synonyms('127.0.0.1','80')
db = syn.db

#
# db.create_user(user='yongsun-cho7i', user_id=1234112323)
# a = db.project('insert',
#               pjt_name='projecthello',
#               user_id=[1234123, 123456],
#               fields=['pjt_name', 'pjt_user'],
#               response_model=ProjectResponse)
#
# b = db.project('insert',
#               pjt_name='nona',
#               user_id=[1234123],
#               fields=['pjt_name', 'pjt_user'],
#               response_model=ProjectResponse)
#
# c = db.cartegory('insert',
#                  cartegory_name='sub_5',
#                  pjt_id=2,
#                  fields=['cartegory_name', 'pjt_id'],
#                  response_model=CategoryResponse)
#
# d = db.origin('insert',
#               pjt_id=1,
#               cartegory_id=1,
#               origin_keyword='lengend2',
#               synm_keyword=['legano2', 'legagnono2'],
#               fields=['pjt_id', 'cartegory_id', 'origin_keyword', 'synonym'],
#               response_model=OriginResponse)

# e = db.synonym('insert',
#                pjt_id=1,
#                cartegory_id=1,
#                origin_id=1,
#                synm_keyword='legano3',
#                fields=['pjt_id', 'cartegory_id', 'origin_id', 'synm_keyword'],
#                response_model=SynonymResponse)



# print(a)
# print(b)
# print(c)
# print(d)
# print(e)


d = db.origin('update',
              id=1,
              origin_keyword='legendsu23232per',
              where=[('id', 'on_off')],
              on_off={"id": True},
              fields=['origin_keyword'],
              response_model=OriginResponse,
              response_preprocess=update_pre_process)

print('origin update', d)

d = db.cartegory('update',
                pjt_id=1,
                id=1,
                cartegory_name= 'sub_123',
                where=[('id', 'on_off')],
                on_off={"id": True},
                fields=['cartegory_name'],
                response_model=CategoryResponse,
                response_preprocess=update_pre_process)

print('cartegory update', d)
print("-"*300)

d = db.origin('find',
              origin_keyword='legendsu23232per',
              where=[('origin_keyword', 'on_off')],
              on_off={"origin_keyword": True},
              response_model=typing.List[OriginResponse])

d = db.origin('find',
              pjt_id=1,
              origin_keyword='legendsu23232per',
              where=[('origin_keyword', 'on_off'), 'and', ('pjt_id', 'on_off')],
              on_off={"origin_keyword": True, "pjt_id": True},
              response_model=typing.List[OriginResponse])
d = db.origin('find',
              pjt_id=1,
              cartegory_id=2,
              origin_keyword='legendsu23232per',
              where=[('origin_keyword', 'on_off'), 'and', ('pjt_id', 'on_off'), 'and', ('cartegory_id', 'on_off')],
              on_off={"origin_keyword": True, "pjt_id": True, "cartegory_id": True},
              response_model=typing.List[OriginResponse])


d = db.cartegory('find',
                pjt_id=2,
                cartegory_name= 'sub_123',
                where=[('pjt_id', 'on_off'), 'and', ('cartegory_name', 'on_off')],
                on_off={"pjt_id": True, "cartegory_name": True},
                response_model=typing.List[CategoryResponse])

d = db.cartegory('find',
                pjt_id=2,
                where=[('pjt_id', 'on_off')],
                on_off={"pjt_id": True},
                response_model=typing.List[CategoryResponse])

# d = db.cartegory('find',
#                 response_model=typing.List[CategoryResponse])

print(d)


# a = db.find_project('find',
#                 user_id='1234123',
#                 pjt_id='1',
#                 where=[('user_id', 'on_off'), 'and', ('pjt_id', 'on_off')],
#                 on_off={'user_id': True,
#                         'pjt_id' : True},
#                 response_model=typing.List[ProjectResponse],
#                 response_preprocess=project_find_post_process)

# b = db.origin('find',
#               response_model=typing.List[OriginResponse])
# print(a)
# print(b)
#
# c = db.update_project(id='1',
#                   pjt_name='sk innovation',
#                   on_off={'id': True},
#                   response_model=typing.List[ProjectResponse])
# print(c)
# # #
# # app = Flask(__name__)
# api = create_synonyms_rest_app(app)
# app.register_blueprint(api)
#
# if __name__ == '__main__':
#     app.run(port=5050)


#Todo 인터페이스 더 깔끔하게 정리하자