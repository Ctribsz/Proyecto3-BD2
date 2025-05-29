from neo4j import GraphDatabase, basic_auth

URI      = "neo4j+s://30fb3bfe.databases.neo4j.io"
USER     = "neo4j"
PASSWORD = "WzIvJUHbQVV8t0WhzMS6TwiQyI_iLlimQ_bqUBGDijQ"

driver = GraphDatabase.driver(URI, auth=basic_auth(USER, PASSWORD))

def get_adyacencias(puzzle_id):
    query = """
    MATCH (p:Pieza)-[:Pertenece]->(r:Rompecabezas {id:$puzzleId})
    OPTIONAL MATCH (p)-[a:Adyacente]-(q:Pieza)
    RETURN
      p.id           AS pieza,
      collect({
        vecino:       q.id,
        mi_lado:      a.lado_pieza_id,
        lado_vecino:  a.conecta_lado_pieza_id
      })             AS adyacentes
    """
    with driver.session() as session:
        result = session.run(query, puzzleId=puzzle_id)
        return {
            rec["pieza"]: rec["adyacentes"]
            for rec in result
        }

def imprimir_desde_pieza(pieza_inicio, adyacencias, piezas_faltantes):
    visitadas = set()
    procesadas = set()

    def dfs(pieza):
        if pieza in visitadas or pieza in piezas_faltantes:
            return
        visitadas.add(pieza)

        print(f"\nPieza {pieza}:")
        for a in adyacencias.get(pieza, []):
            vecino = a['vecino']
            if vecino is None:
                continue

            tupla_relacion = tuple(sorted([pieza, vecino])) + (a['mi_lado'], a['lado_vecino'])

            if tupla_relacion in procesadas:
                continue

            procesadas.add(tupla_relacion)

            if vecino in piezas_faltantes:
                print(f" -- La pieza {vecino} está faltando. Se omite esta conexión.")
                for salto in adyacencias.get(vecino, []):
                    siguiente = salto['vecino']
                    if siguiente and siguiente not in piezas_faltantes and siguiente not in visitadas:
                        dfs(siguiente)
            else:
                print(f"  • está unido con la pieza {vecino} (desde el lado {a['mi_lado']} hacia el lado {a['lado_vecino']} de la otra pieza)")
                dfs(vecino)

    dfs(pieza_inicio)

if __name__ == "__main__":
    puzzle_id = input("ID del rompecabezas (ej. R1): ")
    pieza_inicio = input("ID de la pieza inicial (ej. R1_1): ")

    piezas_faltantes_input = input("Piezas faltantes (separadas por coma, ej. R1_3,R1_5): ")
    piezas_faltantes = set(p.strip() for p in piezas_faltantes_input.split(",") if p.strip())

    adyacencias = get_adyacencias(puzzle_id)
    imprimir_desde_pieza(pieza_inicio, adyacencias, piezas_faltantes)
    driver.close()
