import unittest

from faker import Faker

from src.logica.coleccion import Coleccion
from src.modelo.album import Album
from src.modelo.cancion import Cancion
from src.modelo.declarative_base import Session
from src.modelo.interprete import Interprete


class CancionTestCase(unittest.TestCase):

    def setUp(self):
        self.session = Session()
        self.coleccion = Coleccion()
        # Generación de datos con libreria Faker
        self.data_factory = Faker()

    def test_cancion_sin_interpretes(self):
        # Nombre aleatorio
        titulo_cancion = self.data_factory.name()
        # Número aleatorio entre 0 y 60
        minutos_cancion = self.data_factory.pyint(0, 60)
        segundos_cancion = self.data_factory.pyint(0, 60)
        compositor_cancion = self.data_factory.name()
        cancion = self.coleccion.agregar_cancion(titulo_cancion, minutos_cancion, segundos_cancion, compositor_cancion, -1, [])
        self.assertEqual(cancion, False)

    def test_cancion_varios_interpretes(self):
        nombre_interprete1 = self.data_factory.name()
        # Frase aleatoria
        texto_curiosidades1 = self.data_factory.sentence()
        self.coleccion.agregar_interprete(nombre_interprete1, texto_curiosidades1, -1)
        nombre_interprete2 = self.data_factory.name()
        texto_curiosidades2 = self.data_factory.sentence()
        self.coleccion.agregar_interprete(nombre_interprete2, texto_curiosidades2, -1)
        titulo_cancion = self.data_factory.name()
        minutos_cancion = self.data_factory.pyint(0, 60)
        segundos_cancion = self.data_factory.pyint(0, 60)
        compositor_cancion = self.data_factory.name()
        self.coleccion.agregar_cancion(titulo_cancion, minutos_cancion, segundos_cancion, compositor_cancion, -1,
                                       [{'nombre': nombre_interprete1, 'texto_curiosidades': texto_curiosidades1},
                                        {'nombre': nombre_interprete2,
                                         'texto_curiosidades': texto_curiosidades2}])
        consulta = self.session.query(Cancion).filter(Cancion.titulo == titulo_cancion).first()
        self.assertIsNotNone(consulta)

    def test_editar_cancion(self):
        consulta1 = self.session.query(Cancion).filter(Cancion.id == 2).first().compositor
        consulta2 = self.session.query(Interprete).filter(Interprete.nombre == "Franco de Vita").first()
        texto_curiosidades = self.data_factory.text()
        minutos_cancion = self.data_factory.pyint(0, 60)
        segundos_cancion = self.data_factory.pyint(0, 60)
        if consulta2 is None:
            self.coleccion.agregar_interprete("Franco de Vita", texto_curiosidades, 1)
            self.coleccion.editar_cancion(2, "Bye mamá", minutos_cancion, segundos_cancion, "J.R.Florez y Difelisatti",
                                          [{'id': '2', 'nombre': 'Alejandra Guzman',
                                            'texto_curiosidades': 'Canción dedicada a su ...'},
                                           {'id': 'n', 'nombre': 'Franco de Vita',
                                            'texto_curiosidades': texto_curiosidades}])
        else:
            self.coleccion.editar_cancion(2, "Bye bye", minutos_cancion, segundos_cancion, "J.R.Florez y Difelisatti",
                                          [{'id': '2', 'nombre': 'Alejandra Guzman',
                                            'texto_curiosidades': 'Canción dedicada a su ...'},
                                           {'id': '9', 'nombre': 'Franco de Vita',
                                            'texto_curiosidades': texto_curiosidades}])
        consulta3 = self.session.query(Cancion).filter(Cancion.id == 2).first()
        self.assertEqual(consulta3.compositor, "J.R.Florez y Difelisatti")

    def test_eliminar_cancion(self):
        self.coleccion.eliminar_cancion(3)
        consulta = self.session.query(Cancion).filter(Cancion.id == 3).first()
        self.assertIsNone(consulta)

    def test_dar_cancion_por_id(self):
        consulta = self.coleccion.dar_cancion_por_id(1)
        self.assertEqual(consulta["titulo"], "Baby blues")
