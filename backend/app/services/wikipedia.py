import httpx
from urllib.parse import quote

WIKI_HEADERS = {"User-Agent": "WildInfo/1.0 (proyecto escolar de biodiversidad)"}


async def fetch_wikipedia_resumen(
    nombre_comun: str,
    nombre_cientifico: str = None,
    familia: str = None,
):
    opciones = []

    if nombre_cientifico:
        limpio = nombre_cientifico.strip().lower()
        if limpio:
            limpio = limpio[0].upper() + limpio[1:]
        opciones.append(limpio)

    if nombre_comun:
        opciones.append(nombre_comun.strip())

    if familia:
        f = familia.strip().lower()
        if f:
            f = f[0].upper() + f[1:]
        opciones.append(f)

    async with httpx.AsyncClient(follow_redirects=True) as client:
        # Intento 1: REST API page/summary
        for termino in opciones:
            if not termino:
                continue
            try:
                termino_url = quote(termino.replace(" ", "_"), safe="_")
                url = (
                    "https://es.wikipedia.org/api/rest_v1/page/summary/"
                    f"{termino_url}"
                )
                response = await client.get(url, headers=WIKI_HEADERS, timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    tipo = data.get("type", "")
                    if tipo == "no-extract":
                        continue
                    extracto = data.get("extract")
                    if extracto and "pueden referirse a" not in extracto.lower():
                        return {
                            "resumen": extracto,
                            "enlace_articulo": data.get("content_urls", {})
                            .get("desktop", {})
                            .get("page", "#"),
                        }
            except Exception:
                continue

        # Intento 2: MediaWiki query + redirects (título exacto)
        for termino in opciones:
            if not termino:
                continue
            try:
                st = quote(termino.replace(" ", "_"))
                url = (
                    "https://es.wikipedia.org/w/api.php"
                    "?action=query&prop=extracts&exintro&explaintext"
                    f"&format=json&titles={st}&redirects=1"
                )
                res = await client.get(url, headers=WIKI_HEADERS, timeout=5.0)
                if res.status_code == 200:
                    pages = res.json().get("query", {}).get("pages", {})
                    for pid, pdata in pages.items():
                        if pid != "-1" and "missing" not in pdata and pdata.get("extract"):
                            titulo = pdata.get("title", termino)
                            extracto = pdata["extract"]
                            if len(extracto) > 400:
                                extracto = extracto[:400] + "..."
                            return {
                                "resumen": extracto,
                                "enlace_articulo": (
                                    "https://es.wikipedia.org/wiki/"
                                    f"{quote(titulo.replace(' ', '_'))}"
                                ),
                            }
            except Exception:
                continue

        # Intento 3: Búsqueda por texto libre (generator=search)
        for termino in opciones:
            if not termino:
                continue
            try:
                st = quote(termino)
                url = (
                    "https://es.wikipedia.org/w/api.php"
                    "?action=query&generator=search&gsrlimit=1"
                    "&prop=extracts&exintro&explaintext"
                    "&format=json"
                    f"&gsrsearch={st}"
                )
                res = await client.get(url, headers=WIKI_HEADERS, timeout=5.0)
                if res.status_code == 200:
                    pages = res.json().get("query", {}).get("pages", {})
                    for pid, pdata in pages.items():
                        if pid != "-1" and "missing" not in pdata and pdata.get("extract"):
                            titulo = pdata.get("title", termino)
                            extracto = pdata["extract"]
                            if len(extracto) > 400:
                                extracto = extracto[:400] + "..."
                            return {
                                "resumen": extracto,
                                "enlace_articulo": (
                                    "https://es.wikipedia.org/wiki/"
                                    f"{quote(titulo.replace(' ', '_'))}"
                                ),
                            }
            except Exception:
                continue

    return {
        "resumen": (
            "Información zoológica disponible en el catálogo internacional "
            f"para {nombre_comun}."
        ),
        "enlace_articulo": "#",
    }
