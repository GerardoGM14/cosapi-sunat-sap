import os
import pandas as pd
import asyncio


async def limpiar_duplicados_excel(input_path: str):

    output_path = os.path.join(
        os.path.dirname(input_path),
        f"{os.path.basename(input_path).split('.')[0]}_limpio.xlsx"
    )
    
    def procesar_datos():
        df = pd.read_excel(input_path, dtype=str)

        # 🔑 Columnas que DEFINEN duplicado real
        columnas_clave = [
            'Número de Orden de Compra (OC)',
            'Ruc',
            'Factura',
            'Recepciones',
            'Secuencia de pre-registro'
        ]

        # --- Normalización ---
        for col in columnas_clave:
            df[col] = (
                df[col]
                .fillna("")
                .str.strip()
                .str.upper()
            )

        total = len(df)

        # --- Eliminar duplicados reales ---
        df_limpio = df.drop_duplicates(
            subset=columnas_clave,
            keep='first'
        )

        eliminadas = total - len(df_limpio)

        df_limpio.to_excel(output_path, index=False)
        return eliminadas

    loop = asyncio.get_running_loop()
    filas_eliminadas = await loop.run_in_executor(None, procesar_datos)

    print(f"✅ Filas eliminadas: {filas_eliminadas}")
    return filas_eliminadas


if __name__ == "__main__":
    asyncio.run(
        limpiar_duplicados_excel(
            r'C:\Users\MARKETING\Desktop\ABRAHAN\COSAPI\sap\PE02_Reporte de Contabilidad.xlsx'
        )
    )
