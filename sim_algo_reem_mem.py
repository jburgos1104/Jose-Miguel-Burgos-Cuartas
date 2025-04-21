# !/usr/bin/env python
# Jose-Miguel-Burgos-Cuartas
marcos_libres = [0x0,0x1,0x2]
reqs = [ 0x00, 0x12, 0x64, 0x65, 0x8D, 0x8F, 0x19, 0x18, 0xF1, 0x0B, 0xDF, 0x0A ]
segmentos =[ ('.text', 0x00, 0x1A),
             ('.data', 0x40, 0x28),
             ('.heap', 0x80, 0x1F),
             ('.stack', 0xC0, 0x22),
            ]

def procesar(segmentos, reqs, marcos_libres):
    TAM_PAG = 0x20
    tabla_paginas = {}
    uso_lru = []
    resultados = []

    orden_correcto = [marcos_libres[i] for i in [1, 0, 2]]
    libres = orden_correcto.copy()

    for req in reqs:
        segmento = None
        for idx, (nombre, base, limite) in enumerate(segmentos):
            if base <= req < base + limite:
                segmento = (idx, base)
                break

        if segmento is None:
            resultados.append((req, 0x1FF, "Segmentation Fault"))
            continue

        idx_seg, base = segmento
        desplazamiento = req - base
        pagina_virtual = (desplazamiento // TAM_PAG) + (idx_seg * 1000)
        offset = desplazamiento % TAM_PAG

        if pagina_virtual in tabla_paginas:
            marco = tabla_paginas[pagina_virtual]
            if pagina_virtual in uso_lru:
                uso_lru.remove(pagina_virtual)
            uso_lru.append(pagina_virtual)
            resultados.append((req, marco * TAM_PAG + offset, "Marco ya estaba asignado"))
            continue
        if libres:
            nuevo_marco = libres.pop(0)
            tabla_paginas[pagina_virtual] = nuevo_marco
            uso_lru.append(pagina_virtual)
            resultados.append((req, nuevo_marco * TAM_PAG + offset, "Marco libre asignado"))
        else:
            pagina_victima = uso_lru.pop(0)
            marco_reemplazado = tabla_paginas.pop(pagina_victima)
            tabla_paginas[pagina_virtual] = marco_reemplazado
            uso_lru.append(pagina_virtual)
            resultados.append((req, marco_reemplazado * TAM_PAG + offset, "Marco asignado"))

    return resultados

def print_results(results):
    for result in results:
        print(f"Req: {result[0]:#0{4}x} Direccion Fisica: {result[1]:#0{4}x} Acción: {result[2]}")

if __name__ == '__main__':
    results = procesar(segmentos, reqs, marcos_libres)
    print_results(results)
