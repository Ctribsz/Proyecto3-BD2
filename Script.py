from neo4j import GraphDatabase, basic_auth

# Parámetros de conexión
URI = "neo4j+s://30fb3bfe.databases.neo4j.io"
USER = "neo4j"
PASSWORD = "WzIvJUHbQVV8t0WhzMS6TwiQyI_iLlimQ_bqUBGDijQ"

driver = GraphDatabase.driver(URI, auth=basic_auth(USER, PASSWORD))

def get_adyacencias(puzzle_id):
    query = """
    MATCH (p:Pieza)-[:Pertenece]->(r:Rompecabezas {id:$puzzleId})
    OPTIONAL MATCH (p)-[a:Adyacente]->(q:Pieza)
    RETURN
      p.id AS pieza,
      collect({
        vecino: q.id,
        mi_lado: a.lado_pieza_id,
        lado_vecino: a.conecta_lado_pieza_id
      }) AS adyacentes
    """
    with driver.session() as session:
        result = session.run(query, puzzleId=puzzle_id)
        return {rec["pieza"]: rec["adyacentes"] for rec in result}


class ArmadorRompecabezas:
    def __init__(self, adyacencias, piezas_faltantes):
        self.adyacencias = adyacencias
        self.piezas_faltantes = piezas_faltantes
        self.visitadas = set()
        self.procesadas = set()
        self.pasos = []
        self.paso_actual = 1

    def recorrer(self, pieza):
        if pieza in self.visitadas or pieza in self.piezas_faltantes:
            return
        self.visitadas.add(pieza)

        conexiones = []

        for a in self.adyacencias.get(pieza, []):
            vecino = a["vecino"]
            if not vecino:
                continue

            key = tuple(sorted([pieza, vecino])) + (a['mi_lado'], a['lado_vecino'])
            if key in self.procesadas:
                continue
            self.procesadas.add(key)

            if vecino in self.piezas_faltantes:
                conexiones.append((vecino, a['mi_lado'], a['lado_vecino'], True))
            else:
                conexiones.append((vecino, a['mi_lado'], a['lado_vecino'], False))

        if conexiones:
            self.pasos.append({
                "pieza": pieza,
                "paso": self.paso_actual,
                "conexiones": conexiones
            })
            self.paso_actual += 1

            for vecino, _, _, faltante in conexiones:
                if not faltante:
                    self.recorrer(vecino)

    def imprimir_pasos(self):
        for paso in self.pasos:
            print(f"\nPieza {paso['pieza']} (paso: {paso['paso']})")
            for vecino, mi_lado, lado_vecino, faltante in paso["conexiones"]:
                if faltante:
                    print(f"   -- La pieza {vecino} está faltando. Se omite esta conexión.")
                else:
                    print(f"   • está unido con la pieza {vecino} "
                          f"(desde el lado {mi_lado} hacia el lado {lado_vecino} de la otra pieza)")


if __name__ == "__main__":
    puzzle_id = input("ID del rompecabezas (ej. R1): ")
    pieza_inicio = input("ID de la pieza inicial (ej. R1_1): ")
    faltantes_input = input("Piezas faltantes (separadas por coma, ej. R1_3,R1_5): ")
    piezas_faltantes = {p.strip() for p in faltantes_input.split(",") if p.strip()}

    adyacencias = get_adyacencias(puzzle_id)
    armador = ArmadorRompecabezas(adyacencias, piezas_faltantes)
    armador.recorrer(pieza_inicio)
    armador.imprimir_pasos()
    driver.close()
