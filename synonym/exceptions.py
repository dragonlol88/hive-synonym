# exception & error 정의


__all__ = ['DataBaseModelError',
           'InstanciateError',
           'ImproperlyDataStructureError',
           'ResponseModelError',
           'FilterError',
           'OrderByError']


class DataBaseModelError(Exception):
    """Error related with Database"""


class InstanciateError(DataBaseModelError):
    """sqlalchemy Model Instanciate Error
    500 error
    """

class FilterError(DataBaseModelError):
    """sqlalchemy Improperly made filter error

    """

class OrderByError(DataBaseModelError):
    """sqlalchemy Improperly made order by error
    500 error
    """

class ImproperlyDataStructureError(Exception):
    """Improperly structured data error
    500 error
    """

class ResponseModelError(Exception):
    """Error related with Response Model"""
