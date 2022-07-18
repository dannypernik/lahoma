from app import app, db
from app.models import User, Client

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Client': Client, 'users':User.query.all()}
