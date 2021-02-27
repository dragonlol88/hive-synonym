import re
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

class UserResponse(Response):
    id: int
    user_id: str
    password: str
    created_at: datetime

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
    category_name: str
    pjt_id: int
    created_at: datetime
    updated_at: datetime

class SynonymResponse(Response):
    id: int
    origin_id: int
    pjt_id: int
    category_id: int
    synm_keyword: str
    created_at: datetime

class OriginResponse(Response):

    id: int
    category_id: int
    category_id: int
    origin_keyword: str
    created_at: datetime
    updated_at: datetime
    synonym: typing.List[SynonymResponse]


class SynonymFileOutput(BaseModel):
    origin_keyword: str
    synm_keyword: typing.List[str]

def project_find_pre_process(response, **options):

    pjt_name = options.pop("pjt_name", None)
    if len(response) == 0:
        """검색데이터가 없을 시"""
        raise ValueError

    response = [inst.project for inst in response]
    new_response = []

    if pjt_name:
        #pjt_name 있을 시 pjt_name으로 필터링 하기
        for resp in response:
            is_target = re.search(pjt_name, resp.pjt_name)
            if is_target:
                new_response.append(resp)
        response = new_response
    return sorted(response, key=lambda x: getattr(x, 'updated_at'), reverse=False)


def update_pre_process(response, **options):
    if not response:
        return response
    return response[0]
