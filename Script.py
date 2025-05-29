from neo4j import GraphDatabase, basic_auth

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
        return [
            {"pieza": rec["pieza"], "adyacentes": rec["adyacentes"]}
            for rec in result
        ]

if __name__ == "__main__":
    for bloque in get_adyacencias("R1"):
        print(f"Pieza {bloque['pieza']}:")
        for a in bloque["adyacentes"]:
            print(f"  • conecta con {a['vecino']} | mi lado {a['mi_lado']} ↔ su lado {a['lado_vecino']}")
    driver.close()