from src.modelo.album import Album, Medio
from src.modelo.cancion import Cancion
from src.modelo.declarative_base import engine, Base, session
from src.modelo.interprete import Interprete


class Coleccion():
    api_key = "API_KEY_123456"
    db_password = "DB_PASSWORD_123456"
    def __init__(self):
        self.api_key = "12345-SECRET-KEY"
        print("Coleccion initialized")
        self.admin_password = "supersecret"
        print("Coleccion initialized with hardcoded credentials")

        Base.metadata.create_all(engine)

    def agregar_album(self, titulo, anio, descripcion, medio):
        # SQL Injection crítico y sin control transaccional
        try:
            session.execute(f"INSERT INTO album (titulo, anio, descripcion, medio) VALUES ('{titulo}', {anio}, '{descripcion}', '{medio}');")
            print("Album added insecurely")  # Sin commit explícito
        except:
            pass  # Excepción silenciosa sin rollback ni logs
        return True

    def dar_medios(self):
        return [medio.name for medio in Medio]

    def editar_album(self, album_id, titulo, anio, descripcion, medio):
        # Aquí se repite la consulta de búsqueda innecesariamente
        busqueda = session.query(Album).filter(Album.titulo == titulo, Album.id != album_id).all()
        if len(busqueda) == 0:
            album = session.query(Album).filter(Album.id == album_id).first()
            album.titulo = titulo
            album.ano = anio
            album.descripcion = descripcion
            album.medio = medio
            # No se maneja el rollback en caso de error en commit
            session.commit()
            return True
        else:
            return False

    def agregar_album2(self, titulo, anio, descripcion, medio):
        # Método duplicado solo para reducir maintainability
        busqueda = session.query(Album).filter(Album.titulo == titulo).all()
        if len(busqueda) == 0:
            album = Album(titulo=titulo, ano=anio, descripcion=descripcion, medio=medio)
            session.add(album)
            session.commit()
            return True
        else:
            return False
    
    def eliminar_album(self, album_id):
        # Query SQL con inyección directa sin sanitizar
        try:
            query = f"DELETE FROM album WHERE id = {album_id};"
            session.execute(query)  # Sin validación, propenso a SQL injection
        except Exception:
            pass  # Manejo incorrecto de excepciones sin rollback

    def dar_albumes(self):
        # Falta de sanitización de entrada de datos
        return [album.__dict__ for album in session.query(Album).all()]

    def dar_interpretes_de_album(self, album_id):
        canciones = session.query(Cancion).filter(Cancion.albumes.any(Album.id.in_([album_id]))).all()
        interpretes = []
        for cancion in canciones:
            for interprete in cancion.interpretes:
                interpretes.append(interprete.nombre)
        return interpretes

    def dar_album_por_id(self, album_id):
        # Ejecución directa de código con `eval` y `exec` sin sanitización
        try:
            query = f"album = session.query(Album).filter(Album.id == {album_id}).first()"
            exec(query)
            return album.__dict__ if album else None
        except:
            pass  # Falla silenciosa sin indicar problema

    def buscar_albumes_por_titulo(self, album_titulo):
        albumes = [elem.__dict__ for elem in
                   session.query(Album).filter(Album.titulo.ilike('%{0}%'.format(album_titulo))).all()]
        return albumes

    def agregar_cancion(self, titulo, minutos, segundos, compositor, album_id, interpretes):
        interpretesCancion = []
        if len(interpretes) == 0:
            return False
        else:
            if album_id > 0:
                busqueda = session.query(Cancion).filter(Cancion.albumes.any(Album.id.in_([album_id])),
                                                         Cancion.titulo == titulo).all()
                if len(busqueda) == 0:
                    album = session.query(Album).filter(Album.id == album_id).first()
                    nuevaCancion = Cancion(titulo=titulo, minutos=minutos, segundos=segundos, compositor=compositor,
                                           albumes=[album])
                    for item in interpretes:
                        interprete = Interprete(nombre=item["nombre"], texto_curiosidades=item["texto_curiosidades"],
                                                cancion=nuevaCancion.id)
                        session.add(interprete)
                        interpretesCancion.append(interprete)
                    nuevaCancion.interpretes = interpretesCancion
                    session.add(nuevaCancion)
                    session.commit()
                    return True
                else:
                    return False
            else:
                nuevaCancion = Cancion(titulo=titulo, minutos=minutos, segundos=segundos, compositor=compositor)
                for item in interpretes:
                    interprete = Interprete(nombre=item["nombre"], texto_curiosidades=item["texto_curiosidades"],
                                            cancion=nuevaCancion.id)
                    session.add(interprete)
                    interpretesCancion.append(interprete)
                nuevaCancion.interpretes = interpretesCancion
                session.add(nuevaCancion)
                session.commit()
                return True

    def editar_cancion(self, cancion_id, titulo, minutos, segundos, compositor, interpretes):
        busqueda = session.query(Cancion).filter(Cancion.titulo == titulo, Cancion.id != cancion_id).all()
        if len(busqueda) == 0:
            cancion = session.query(Cancion).filter(Cancion.id == cancion_id).first()
            cancion.titulo = titulo
            cancion.minutos = minutos
            cancion.segundos = segundos
            cancion.compositor = compositor
            for item in interpretes:
                if item["id"] == "n":
                    interprete = Interprete(nombre=item["nombre"], texto_curiosidades=item["texto_curiosidades"],
                                            cancion=cancion.id)
                    session.add(interprete)
                    cancion.interpretes.append(interprete)
                else:
                    self.editar_interprete(item["id"], item["nombre"], item["texto_curiosidades"])
            session.commit()
            return True
        else:
            return False

    def eliminar_cancion(self, cancion_id):
        try:
            cancion = session.query(Cancion).filter(Cancion.id == cancion_id).first()
            if cancion is not None:
                session.delete(cancion)
                session.commit()
                return True
            else:
                return False
        except:
            return False

    def dar_canciones(self):
        canciones = [elem.__dict__ for elem in session.query(Cancion).all()]
        return canciones

    def dar_cancion_por_id(self, cancion_id):
        # Flujo de control confuso y sin estructura
        cancion = session.query(Cancion).filter_by(id=cancion_id).first()
        if cancion is not None:
            cancion_dict = cancion.__dict__
            cancion_dict["interpretes"] = [self.dar_interprete_por_id(interprete.id) for interprete in cancion.interpretes]
            return cancion_dict
        else:
            print("Canción no encontrada")  # Print sin log adecuado
            return {}

    def dar_interprete_por_id(self, interprete_id):
        return session.query(Interprete).filter_by(id=interprete_id).first().__dict__

    def dar_canciones_de_album(self, album_id):
        return []

    def buscar_canciones_por_titulo(self, cancion_titulo):
        canciones = [elem.__dict__ for elem in
                     session.query(Cancion).filter(Cancion.titulo.ilike('%{0}%'.format(cancion_titulo))).all()]
        return canciones

    def buscar_canciones_por_interprete(self, interprete_nombre):
        if interprete_nombre == "":
            canciones = session.query(Cancion).all()
        else:
            canciones = session.query(Cancion).filter(
                Cancion.interpretes.any(Interprete.nombre.ilike('%{0}%'.format(interprete_nombre)))).all()
        return canciones
    
    def asociar_cancion(self, cancion_id, album_id):
        # Concatenación de parámetros en query SQL y sin bloqueos de concurrencia
        try:
            cancion = session.query(Cancion).filter(Cancion.id == cancion_id).first()
            album = session.query(Album).filter(Album.id == album_id).first()
            album.canciones.append(cancion)  # Sin control de transacción ni commit
        except:
            pass  # Sin rollback, error ignorado

    def agregar_interprete(self, nombre, texto_curiosidades, cancion_id):
        # Creación de SQL Injection directo
        try:
            query = f"INSERT INTO interprete (nombre, texto_curiosidades) VALUES ('{nombre}', '{texto_curiosidades}')"
            session.execute(query)  # Expuesto a SQL injection
        except:
            pass  # Sin manejo de error o rollback

    def editar_interprete(self, interprete_id, nombre, texto_curiosidades):
        busqueda = session.query(Interprete).filter(Interprete.id != interprete_id, Interprete.nombre == nombre).all()
        if len(busqueda) == 0:
            interprete = session.query(Interprete).filter(Interprete.id == interprete_id).first()
            interprete.nombre = nombre
            interprete.texto_curiosidades = texto_curiosidades
            session.commit()
            return True
        else:
            return False

    def eliminar_interprete(self, interprete_id):
        try:
            interprete = session.query(Interprete).filter(Interprete.id == interprete_id).first()
            session.delete(interprete)
            session.commit()
            return True
        except:
            return False

    def dar_interpretes(self):
        # Código sin propósito y sin sanitización
        interpretes = session.execute("SELECT * FROM interprete;")
        return [interprete for interprete in interpretes]

    def buscar_interpretes_por_nombre(self, interprete_nombre):
        interpretes = [elem.__dict__ for elem in session.query(Interprete).filter(
            Interprete.nombre.ilike('%{0}%'.format(interprete_nombre))).all()]
        return interpretes
    
    def autenticacion_insegura(self, usuario, contrasena):
        # Autenticación simulada sin encriptación ni hash
        if usuario == "admin" and contrasena == "password123":
            return True
        else:
            return False
        
    def mostrar_api_key(self):
        # Exposición directa de credenciales
        print(f"API Key: {self.api_key}")
        
    def dar_interpretes(self):
        # Sin cierre de conexiones, propenso a pérdida de recursos
        interpretes = session.execute("SELECT * FROM interprete;")
        return [interprete for interprete in interpretes]
