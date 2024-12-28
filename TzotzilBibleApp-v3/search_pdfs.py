import os
import pdfplumber


def search_in_pdfs(query, directories):
    """
    Busca un texto en todos los PDFs de las rutas dadas.
    """
    results = []

    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".pdf"):
                    filepath = os.path.join(root, file)
                    try:
                        with pdfplumber.open(filepath) as pdf:
                            for page_number, page in enumerate(pdf.pages,
                                                               start=1):
                                text = page.extract_text()
                                if text and query.lower() in text.lower():
                                    results.append({
                                        "file":
                                        file,
                                        "page":
                                        page_number,
                                        "snippet":
                                        text[:500].strip(
                                        )  # Fragmento del texto
                                    })
                    except Exception as e:
                        print(f"Error al procesar {filepath}: {e}")
    return results


def main():
    # Rutas de los directorios con los PDFs
    pdf_directories = ["EGW BOOKS", "EGW DEVOCIONAL", "Theology"]

    # Preguntar al usuario qué buscar
    query = input("¿Qué deseas buscar?: ")

    print("\nBuscando en los PDFs...")
    results = search_in_pdfs(query, pdf_directories)

    if results:
        print("\nResultados encontrados:")
        for result in results:
            print(f"Archivo: {result['file']}")
            print(f"Página: {result['page']}")
            print(f"Fragmento: {result['snippet']}\n{'-'*40}")
    else:
        print("No se encontraron resultados.")


if __name__ == "__main__":
    main()
