# Configuración de Argumentos

Este proyecto ofrece dos métodos para proporcionar los argumentos de configuración necesarios para su ejecución: a través de la línea de comandos o mediante un archivo de variables de entorno (`.env`).

## Gestor de Configuración

El módulo `src/config/manager_args.py` se encarga de determinar qué método de configuración utilizar. Por defecto, utiliza el método de variables de entorno.

Para cambiar el método, se puede establecer la variable de entorno `CONFIG_METHOD`:

- `env` (por defecto): Utiliza las variables de entorno (recomendado para producción).
- `console`: Utiliza los argumentos pasados por la línea de comandos.

## 1. Uso a través de Variables de Entorno (`.env`)

Este es el método recomendado, especialmente para entornos de producción, ya que evita exponer datos sensibles en la línea de comandos.

### Pasos

1. Crea un archivo llamado `.env` en la raíz del proyecto (`d:\\cosapi\\.env`).
2. Añade las siguientes variables al archivo con sus respectivos valores:

    ```env
    FOLDER="d:\\cosapi\\output"
    CODE_SOCIEDAD="PE01"
    DATE="17/01/2026"
    RUC_SUNAT="12345678901"
    USER_SUNAT="testuser"
    PASSWORD_SUNAT="testpass"
    CORREO_SAP="test@sap.com"
    PASSWORD_SAP="sappass"
    ```

3. El script leerá automáticamente estas variables al ejecutarse.

## 2. Uso a través de la Línea de Comandos

Este método es útil para pruebas rápidas o desarrollo. Los argumentos se pasan directamente al ejecutar el script.

### Ejemplo de uso

```bash
python main.py --folder "C:\Users\MARKETING\Desktop\ABRAHAN\COSAPI" --code_sociedad "PE01" --date "17/01/2026" --ruc_sunat "20100082391" --user_sunat "JAUREGUI" --password_sunat "Dante123*" --correo_sap "dantejauregui@sertech.pe" --password_sap "SapMty_2026" --socket_url "ws://localhost:3000"
```

Asegúrate de que el gestor de configuración (`manager_args.py`) esté configurado para usar el método `console` si deseas utilizar esta opción.
