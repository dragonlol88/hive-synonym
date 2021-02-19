import typing
from pydantic import BaseModel
from datetime import datetime

class Response(BaseModel):

    class Config:
        orm_mode = True

    def __init__(self, **data: typing.Any):
        super().__init__(**data)

    @classmethod
    def post_process(cls, resp):
        """
        데이터가 들어가기 전에 전처리 하기
        :param resp:
        :return:
        """
        return resp


class ProjectResponse(Response):
    id: int
    pjt_name: str
    created_at: datetime
    updated_at: datetime

class ProjectUserResponse(Response):
    id : int
    user_id: int
    pjt_id: int
    project: ProjectResponse

class CategoryResponse(Response):

    id: int
    cartegory_name: str
    pjt_id: int
    created_at: datetime
    updated_at: datetime

class SynonymResponse(Response):
    id: int
    origin_id: int
    pjt_id: int
    cartegory_id: int
    synm_keyword: str
    created_at: datetime

class OriginResponse(Response):

    id: int
    cartegory_id: int
    origin_keyword: str
    created_at: datetime
    updated_at: datetime
    synonym: typing.List[SynonymResponse]

def project_find_post_process(response):

    if len(response) == 0:
        """검색데이터가 없을 시"""
        raise ValueError

    response = [getattr(inst, 'project') for inst in response]

    return sorted(response, key=lambda x: getattr(x, 'updated_at'), reverse=False)


def update_pre_process(response):
    if not response:
        return response
    return response[0]
