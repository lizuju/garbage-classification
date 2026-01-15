from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# 延迟绑定：在 create_app 中 init_app
db = SQLAlchemy()
cors = CORS()

