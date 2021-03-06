# -*- coding: utf-8 -*-

import datetime
import transaction
import zope.schema

from barrel import cooper
from cromlech.dawnlight import DawnlightPublisher, ViewLookup
from cromlech.i18n.utils import setLanguage
from cromlech.security import Interaction
from cromlech.sqlalchemy import (
    SQLAlchemySession, create_engine, create_and_register_engine)
from cromlech.webob import Request
from dolmen.sqlcontainer import SQLContainer
from sqlalchemy import Column, Text, Integer, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from ul.auth import require
from uvc.themes.btwidgets import IBootstrapRequest
from uvclight import eval_loader, query_view
from uvclight import setSession, IRootObject
from uvclight.directives import traversable
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface, implementer, alsoProvides
from zope.location import Location
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


_ = MessageFactory("gatekeeper")


def query(request, obj, name):
    return query_view(request, obj, name=name)


view_lookup = ViewLookup(query)

Admin = declarative_base()


ALERT = u"alert"
INFO = u"infos"
ADVERT = u"advert"

ON_DATES = u"on_dates"
DISABLED = u"disabled"
ENABLED = u"enabled"


MODES = SimpleVocabulary((
    SimpleTerm(title=_("Always", default="Always"), value=ENABLED),
    SimpleTerm(title=_("Time span", default="Time span"), value=ON_DATES),
    SimpleTerm(title=_("Disabled", default="Disabled"), value=DISABLED),
    ))


TYPES = SimpleVocabulary((
    SimpleTerm(title=_("Alert", default="Alert"), value=ALERT),
    SimpleTerm(title=_("Info", default="Information"), value=INFO),
    SimpleTerm(title=_("Ad", default="Advertisment"), value=ADVERT),
    ))


styles = {
    ALERT: u"alert alert-error",
    INFO: u"alert",
    ADVERT: u"alert alert-info",
    }


def now():
    return datetime.datetime.now()


class IMessage(Interface):

    id = zope.schema.Int(
        title=_("Unique identifier"),
        readonly=True,
        required=True)

    message = zope.schema.Text(
        title=_("Message"),
        required=True)

    type = zope.schema.Choice(
        title=_("Type of message"),
        vocabulary=TYPES,
        default=INFO,
        required=True)

    activation = zope.schema.Choice(
        title=_("Method of activation"),
        vocabulary=MODES,
        default=ON_DATES,
        required=True)

    enable = zope.schema.Datetime(
        title=_(u"Date of activation"),
        description=_(u"Set empty for an immediate activation"),
        required=False)

    disable = zope.schema.Datetime(
        title=_(u"Date of de-activation"),
        description=_(u"Set empty for an immediate de-activation"),
        required=False)


class Message(Location, Admin):
    require('zope.Public')

    __tablename__ = 'messages'

    id = Column('id', Integer, primary_key=True)
    message = Column('message', Text, nullable=False)
    type = Column('type', String(32), nullable=False)
    activation = Column('activation', String(32), nullable=False)
    enable = Column('enable', DateTime, nullable=False, default=now())
    disable = Column('disable', DateTime, nullable=False, default=now())


class MessagesRoot(SQLContainer):
    factory = model = Message


@implementer(IRootObject)
class AdminRoot(Location):
    traversable('messages')

    def __init__(self, pkey, dbkey):
        self.pkey = pkey
        self.messages = MessagesRoot(self, 'messages', dbkey)


def get_valid_messages(session):
    limit = now()
    enabled = session.query(Message).filter(Message.activation == ENABLED)
    valid = session.query(Message).filter(
        Message.activation == ON_DATES).filter(
        Message.enable <= limit).filter(Message.disable >= limit)
    return iter(enabled.union(valid))


admins = [
    ('admin', 'admin'),
    ]

REALM = "sso.novareto.de"


def admin(global_conf, dburl, dbkey, pkey, session_key, layer=None, **kwargs):

    engine = create_and_register_engine(dburl, dbkey)
    engine.bind(Admin)
    Admin.metadata.create_all()

    root = AdminRoot(pkey, dbkey)
    publisher = DawnlightPublisher(view_lookup=view_lookup)
    
    @cooper.basicauth(users=admins, realm=REALM)
    def app(environ, start_response):
        session = environ[session_key].session
        setSession(session)
        setLanguage('de')
        request = Request(environ)
        alsoProvides(request, IBootstrapRequest)
        if layer:
            skin_layer = eval_loader(layer)
            alsoProvides(request, skin_layer)
        with Interaction():
            with transaction.manager as tm:
                with SQLAlchemySession(engine, transaction_manager=tm):
                    response = publisher.publish(
                        request, root, handle_errors=True)
                    result = response(environ, start_response)
        setSession()
        return result
    return app


def messages_injector(app, global_conf, dburl, envkey):
    engine = create_engine(dburl, 'messages')
    Admin.metadata.create_all(engine.engine)

    def message_aware(environ, start_response):
        with SQLAlchemySession(engine) as session:
            messages = get_valid_messages(session)
        book = environ.setdefault(envkey, {})
        admin = book.setdefault('admin', [])
        admin.extend(messages)
        return app(environ, start_response)

    return message_aware
