#import logging

from flask import Flask, session
from datetime import timedelta, datetime

app = Flask(__name__, static_folder='static')
app.url_map.strict_slashes = False

from configs.config import Config_

# logging.basicConfig(
#     level = logging.WARNING,
#     format= '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s | %(lineno)d | %(message)s | %(pathname)s',
#     filename=Config.LoggingFiles.for_flask,
#     filemode='a'
# )

app.config['SECRET_KEY'] = "6xP5eaesdsjhmeVbSJrCrzK4mxwmgWWdOTLg9lN"
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

app.config['SECURITY_HEADERS'] = True
app.config['X_FRAME_OPTIONS'] = 'SAMEORIGIN'
app.config['STRICT_TRANSPORT_SECURITY'] = True
app.config['CONTENT_SECURITY_POLICY'] = True
app.config['X_CONTENT_TYPE_OPTIONS'] = 'nosniff'
app.config['X_XSS_PROTECTION'] = '1; mode=block'

app.permanent_session_lifetime = timedelta(days=365)

@app.before_request
def permanent_session():
    session.permanent = True


from .index.indexr import index_
from .admin.adminr import admin

app.register_blueprint(index_, url_prefix='/')
app.register_blueprint(admin, url_prefix='/admin')

def format_date(value, format='%d %B %Y'):
    if value is None:
        return ""
    if isinstance(value, str):
        value = datetime.strptime(value, '%Y-%m-%d')
    return value.strftime(format)

# Enregistrez le filtre dans votre app Flask
app.jinja_env.filters['date'] = format_date