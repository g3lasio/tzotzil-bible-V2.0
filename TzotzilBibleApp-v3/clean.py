import pandas as pd
import re

# Rutas del archivo existente y para guardar el archivo limpio en la raíz del proyecto
input_path = "zotzil bible100%limpio.csv"
output_path = "zotzil_bible100%limpio_cleaned.csv"

# Cargar el DataFrame existente
df = pd.read_csv(input_path)


# Definir función para limpiar caracteres específicos
def clean_text_tzotzil(text):
    if pd.isna(text):
        return text

    # Utilizar expresión regular para eliminar caracteres no deseados
    unwanted_pattern = r'[^\w\s\u2019áéíóúüñ.,!?\'-]'  # Mantener caracteres alfabéticos, dígitos, algunos signos de puntuación y tildes
    cleaned_text = re.sub(unwanted_pattern, '', text)

    return cleaned_text


# Aplicar la función a la columna de Tzotzil
df['Texto Tzotzil'] = df['Texto Tzotzil'].apply(clean_text_tzotzil)

# Guardar el archivo limpio
df.to_csv(output_path, index=False, encoding='utf-8')

print(f"Archivo limpio guardado en: {output_path}")
