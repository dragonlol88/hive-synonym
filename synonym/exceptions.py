# exception & error 정의


__all__ = ['ConnectionError',
           'InstanciateError',
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

class ConnectionError(BaseException):

    """
    related with sqlalchemy error
    """

class InstanciateError(ConnectionError):
    """sqlalchemy Model Instanciate Error
    """

class FilterError(ConnectionError):
    """sqlalchemy Improperly made filter error
    """

class OrderByError(ConnectionError):
    """sqlalchemy Improperly made order by error
    """

class UpdateError(ConnectionError):
    """sqlalchemy Improperly made order by error
    """


class ImproperlyDataStructureError(BaseException):
    """Improperly structured data error
    """


class ResponseError(BaseException):
    """Error related with Response Model"""


class ResponseModelError(ResponseError):
    """Error related with Response Model"""

class DeserializerError(ResponseError):
    """Deserializer Error"""