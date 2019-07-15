from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import NullPool

from db_conf import db_conf

engine = create_engine(f"mysql+pymysql://"
                       f"{db_conf['db_user']}:{db_conf['db_user_pass']}@"
                       f"{db_conf['host']}/{db_conf['db_name']}?"
                       f"use_unicode=True&charset=utf8&binary_prefix=true",
                       poolclass=NullPool)

db_session = scoped_session(sessionmaker(autocommit=True,
                                         autoflush=True,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


# convert sqlalchemy to json
def as_dict(model):
    return {c.name: getattr(model, c.name) for c in model.__table__.columns}


def required_fields(model, values):
    """
    remove all fields which not exist in model
    :param model:
    :param values: fields from form
    :return:
    """
    if values:
        for k in list(values):
            if k not in model.__table__.columns.keys():
                values.pop(k)
    return values


def init_db():
    import models
    Base.metadata.create_all(bind=engine)
