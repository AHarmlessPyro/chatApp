from app.model import UserModel, MessageModel
from app import db
from app import create_app, socketio

app = create_app(debug=True)

if __name__ == '__main__':
    socketio.run(app)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': UserModel, 'Message': MessageModel}
