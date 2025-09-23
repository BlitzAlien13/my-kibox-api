from KIBox import KIBox, FakeNews
from db_service import DatabaseService
from auth_service import AuthService

# Hier werden die Instanzen nur einmal erzeugt
kibox = KIBox(kibox_instance=None)
db = DatabaseService(kibox_instance=None)
auth = AuthService(db=db)
news = FakeNews(kibox_instance=kibox, auth_service=auth)
