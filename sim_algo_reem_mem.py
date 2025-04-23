marcos_libres = [0x0, 0x1, 0x2]
reqs = [0x00, 0x12, 0x64, 0x65, 0x8D, 0x8F, 0x19, 0x18, 0xF1, 0x0B, 0xDF, 0x0A]
segmentos = [
    ('.text', 0x00, 0x1A),
    ('.data', 0x40, 0x28),
    ('.heap', 0x80, 0x1F),
    ('.stack', 0xC0, 0x22),
]

def procesar(segmentos, reqs, marcos_libres):
    TAM_PAG = 0x10
    tabla_marcos = {}
    tiempos_lru = {}
    contador = 0
    resultados = []

    for dir_logica in reqs:
        contador += 1

        if not any(base <= dir_logica < base + largo for _, base, largo in segmentos):
            resultados.append((dir_logica, 0x1FF, "Segmentation Fault"))
            continue

        pagina_virtual = dir_logica >> 4
        offset = dir_logica & 0xF

        if pagina_virtual in tabla_marcos:
            marco_asignado = tabla_marcos.get(pagina_virtual)
            tiempos_lru[pagina_virtual] = contador
            resultados.append((dir_logica, (marco_asignado << 4) + offset, "Marco ya estaba asignado"))
            continue

        if marcos_libres:
            marco_libre = marcos_libres.pop(0)
            tabla_marcos[pagina_virtual] = marco_libre
            tiempos_lru[pagina_virtual] = contador
            resultados.append((dir_logica, (marco_libre << 4) + offset, "Marco libre asignado"))
        else:
            victima_lru = min(tiempos_lru.items(), key=lambda x: x[1])[0]
            marco_reutilizado = tabla_marcos.pop(victima_lru)
            tiempos_lru.pop(victima_lru)
            tabla_marcos[pagina_virtual] = marco_reutilizado
            tiempos_lru[pagina_virtual] = contador
            resultados.append((dir_logica, (marco_reutilizado << 4) + offset, "Marco asignado"))

    return resultados

def print_results(resultados):
    for req, direccion_fisica, mensaje in resultados:
        print(f"Req: {req:#04x} Direccion Fisica: {direccion_fisica:#04x} Acción: {mensaje}")

if __name__ == '__main__':
    resultados = procesar(segmentos, reqs, marcos_libres)
    print_results(resultados)
