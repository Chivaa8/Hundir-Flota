import random


def generar_barcos_clasicos(filas: int, columnas: int):
    barcos_clasicos = [
        {"nombre": "submarino", "tamaño": 1, "cantidad": 1},
        {"nombre": "destructor", "tamaño": 2, "cantidad": 1},
        {"nombre": "crucero", "tamaño": 3, "cantidad": 1},
        {"nombre": "acorazado", "tamaño": 4, "cantidad": 1},
        {"nombre": "portaaviones", "tamaño": 5, "cantidad": 1},
    ]

    total_casillas = filas * columnas
    casillas_objetivo = int(total_casillas * 0.30)  

    tablero = [[0 for _ in range(columnas)] for _ in range(filas)]
    barcos_colocados = []
    casillas_ocupadas = 0
    id_barco = 1

    for barco in barcos_clasicos:
        for _ in range(barco["cantidad"]):
            posiciones = colocar_barco(tablero, filas, columnas, barco["tamaño"], id_barco)
            if posiciones:
                barcos_colocados.append(
                    {
                        "id": id_barco,
                        "nombre": barco["nombre"],
                        "tamaño": barco["tamaño"],
                        "posiciones": posiciones,
                        "tocado": [False] * barco["tamaño"],
                        "hundido": False,
                    }
                )
                casillas_ocupadas += barco["tamaño"]
                id_barco += 1

    while casillas_ocupadas < casillas_objetivo:
        tamaño_aleatorio = random.randint(1, 5)

        if casillas_ocupadas + tamaño_aleatorio > casillas_objetivo:
            tamaño_aleatorio = casillas_objetivo - casillas_ocupadas
            if tamaño_aleatorio == 0:
                break

        posiciones = colocar_barco(tablero, filas, columnas, tamaño_aleatorio, id_barco)
        if posiciones:
            barcos_colocados.append(
                {
                    "id": id_barco,
                    "nombre": f"barco_extra_{id_barco}",
                    "tamaño": tamaño_aleatorio,
                    "posiciones": posiciones,
                    "tocado": [False] * tamaño_aleatorio,
                    "hundido": False,
                }
            )
            casillas_ocupadas += tamaño_aleatorio
            id_barco += 1
        else:
            break

    porcentaje_ocupacion = (casillas_ocupadas / total_casillas) * 100

    return {
        "barcos": barcos_colocados,
        "tablero": tablero,
        "casillas_ocupadas": casillas_ocupadas,
        "porcentaje_ocupacion": round(porcentaje_ocupacion, 2),
    }


def colocar_barco(tablero, filas: int, columnas: int, tamaño: int, id_barco: int):
    for _ in range(100):
        horizontal = random.choice([True, False])

        if horizontal:
            fila = random.randint(0, filas - 1)
            col_inicio = random.randint(0, columnas - tamaño)
            posiciones = [(fila, col_inicio + i) for i in range(tamaño)]
        else:
            fila_inicio = random.randint(0, filas - tamaño)
            col = random.randint(0, columnas - 1)
            posiciones = [(fila_inicio + i, col) for i in range(tamaño)]

        if puede_colocar_barco(tablero, posiciones):
            for f, c in posiciones:
                tablero[f][c] = id_barco
            return [{"fila": f, "columna": c} for f, c in posiciones]

    return None


def puede_colocar_barco(tablero, posiciones):
    filas = len(tablero)
    columnas = len(tablero[0])

    for fila, col in posiciones:
        if fila < 0 or fila >= filas or col < 0 or col >= columnas:
            return False

        # separación 1 casilla
        for df in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nf = fila + df
                nc = col + dc
                if 0 <= nf < filas and 0 <= nc < columnas and tablero[nf][nc] != 0:
                    return False

    return True
