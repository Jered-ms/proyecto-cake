class User:
    def __init__(self,nombre,rut,correo,rol):
        self.nombre = str(nombre.lower())
        self.rut = str(rut)
        self.correo = str(correo)
        self.rol = str(rol)

""" jered = User("jered","20189898-6","jered.menares@usach.cl","usuario")
print(jered.rut)
jered=jered.lower() """

class Admin:
    def __init__(self):
        self.rut = '21974416-1'
        self.clave = 'pasteleria2197'