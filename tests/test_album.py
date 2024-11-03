import unittest

from faker import Faker

from src.logica.coleccion import Coleccion
from src.modelo.album import Album
from src.modelo.declarative_base import Session


class AlbumTestCase(unittest.TestCase):

    def setUp(self):
        self.session = Session()
        self.coleccion = Coleccion()
        # Generación de datos con libreria Faker
        self.data_factory = Faker()

    def test_editar_album(self):
        nueva_descripcion_album = self.data_factory.sentence()
        self.coleccion.editar_album(2, "Clara luna-Mix", 2013, nueva_descripcion_album, "DISCO")
        consulta = self.session.query(Album).filter(Album.id == 2).first()
        self.assertIsNot(consulta.titulo, "Live Killers")

    def test_eliminar_album(self):
        self.coleccion.eliminar_album(1)
        consulta = self.session.query(Album).filter(Album.id == 1).first()
        self.assertIsNone(consulta)


