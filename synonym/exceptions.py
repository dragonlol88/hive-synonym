# exception & error 정의


__all__ = ['DBConnectionError',
           'ImproperlyDataStructureError',
           'ResponseModelError',
           'FilterError',
           'OrderByError']

class BaseException(Exception):

    @property
    def error(self):
        return self.args[0]

    @property
    def info(self):
        return self.args[1]


# db exceptions
class DBConnectionError(BaseException):
    """related with sqlalchemy error"""


class DBFieldTypeError(DBConnectionError):
    """related with sqlalchemy error"""


class FilterError(DBConnectionError):
    """sqlalchemy Improperly made filter error"""


class OrderByError(DBConnectionError):
    """sqlalchemy Improperly made order by error"""


class UpdateError(DBConnectionError):
    """sqlalchemy Improperly made order by error"""


class DeleteError(DBConnectionError):
    """sqlalchemy Improperly made order by error"""


# response error
class ImproperlyDataStructureError(BaseException):
    """Improperly structured data error"""


class ResponseError(BaseException):
    """Error related with Response Model"""


class ResponseModelError(ResponseError):
    """Error related with Response Model"""


class DeserializerError(ResponseError):
    """Deserializer Error"""