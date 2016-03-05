from app import db
db.drop_all()
db.create_all()

""">>> from piro import db
configuring now
>>> from piro.models import User
>>> admin=User('admin','admin','admin@piro.com')
>>> db.session.add(admin)
[5]+  Stopped                 python
aditya@tyrionLannister:~/berkeleyhackers/piro/piro$ python
Python 2.7.3 (default, Jun 22 2015, 19:33:41) 
[GCC 4.6.3] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> from piro import db
configuring now
>>> db.drop_all()
>>> db.create_all()
>>> from piro.models import User
>>> admin=User('admin','admin','admin@piro.com')
>>> db.session.add(admin)
>>> db.session.commit()"""
