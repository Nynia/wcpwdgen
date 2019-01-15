import os
from app import create_app
from flask_script import Manager, Shell, Server
from flask_migrate import Migrate, MigrateCommand
from app.models import *

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

manager.add_command("runserver", Server('0.0.0.0', '80'))

@manager.command
def deploy():
    """Run deployment tasks."""
    from flask.ext.migrate import upgrade
    upgrade()


if __name__ == '__main__':
    manager.run()
