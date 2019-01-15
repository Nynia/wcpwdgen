### 使用方法
1. 安装virtualenv
```
virtualenv venv
```
2. 安装依赖包
```
source venv/bin/activate (windows不一样)
pip install -r requirements.txt
```
> 如果用到MySQL，Mysqldb需要另外安装，安装方法见另外文档

### 多数据库配置
1. 在config中添加BINDS
```
SQLALCHEMY_BINDS = {
        'ismp': 'mysql://root:admin@127.0.0.1/test'
    }
```
2. 在models中添加__bind_key__
```
class User(db.Model):
    __bind_key__ = 'ismp'
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)

```
3. Migrate配置
```
python manage.py db init --multidb (多个数据库)
python manage.py db migrate
python manage.py db upgrade
```
> tips 可重写upgrade和downgrade方法

### 启动方法
```
python manage.py runserver
```
> ip和port可配置