from typing import List

class TextTypeIdentifier:
    """Clase para identificar el tipo de texto bíblico basado en palabras clave."""

    def __init__(self):
        """Inicializa las categorías de texto con palabras clave relevantes."""
        self.categories = {
            "narrativa": [
                "historia", "evento", "rey", "batalla", "profeta", "viaje", "exilio",
                "milagro", "juicio", "guerra", "rey david", "éxodo", "genealogía", 
                "reino", "derrota", "triunfo", "pueblo", "dios israel", "arca",
                "desierto", "tabernáculo", "sacerdote", "sacrificio", "israel", "templo"
            ],
            "profecía": [
                "visión", "bestia", "dragón", "cuernos", "día-año", "apocalipsis",
                "daniel", "anticristo", "ángel", "sello", "trono", "tribulación",
                "reino eterno", "fin del tiempo", "revelación", "templo celestial",
                "almas", "resurrección", "desolación", "juicio final", "nueva jerusalén",
                "trompeta", "plaga", "reino", "hijo del hombre"
            ],
            "parábola": [
                "parábola", "sembrador", "talentos", "oveja", "moneda", "banquete",
                "fiesta", "trigo", "cizaña", "rey", "deudor", "fiel", "siervo",
                "lámparas", "aceite", "semilla", "mostaza", "levadura", "pescador",
                "tesoro", "campo", "perla", "siembra", "herencia", "hijo pródigo"
            ],
            "poesía": [
                "salmo", "cántico", "poesía", "alabanza", "proverbios", "sabiduría",
                "adoración", "dios", "justo", "pecador", "aleluya", "gloria",
                "creación", "temor", "refugio", "fortaleza", "poder", "majestad",
                "santidad", "redentor", "cántico nuevo", "montes", "mares", "cielo",
                "justicia", "bondad"
            ],
            "epístola": [
                "carta", "iglesia", "mensaje", "hermanos", "enseñanza", "pablo",
                "juan", "pedro", "apóstol", "iglesias", "amor", "fe", "esperanza",
                "gracia", "dios padre", "cristiano", "persecución", "corintios",
                "galacia", "filipos", "hermanos en cristo", "justificación", "salvación",
                "exhortación", "unidad", "doctrina", "obediencia"
            ]
        }

    def identify(self, query: str) -> str:
        """
        Identifica el tipo de texto basado en palabras clave de la consulta.
        :param query: La consulta proporcionada por el usuario.
        :return: El tipo de texto identificado o "desconocido".
        """
        query_lower = query.lower()
        for text_type, keywords in self.categories.items():
            if any(keyword in query_lower for keyword in keywords):
                return text_type
        return "desconocido"
