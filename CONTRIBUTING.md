# Guía de Contribución

¡Gracias por tu interés en contribuir a **Transfer Genius**!  Este
documento describe el proceso y las normas para colaborar de manera
efectiva y mantener la calidad del código.

## Cómo empezar

1. **Fork y clona** el repositorio en tu cuenta de GitHub.
2. Crea una rama a partir de `main` para tu cambio:
   ```bash
   git checkout -b feature/mi-mejora
   ```
3. Instala las dependencias y ejecuta las pruebas para asegurarte de
   que todo funciona antes de modificar:
   ```bash
   make setup
   make test
   ```

## Estilo y calidad de código

Este proyecto utiliza **ruff**, **black** y **mypy** para mantener un
estilo consistente.  Antes de abrir un pull request asegúrate de que
tus cambios pasan las comprobaciones:

```bash
make lint
```

Además:

* Sigue las normas de PEP 8 en lo que no contradiga a `black`.
* Escribe tipado estático siempre que sea posible.
* Maneja errores con `try/except` y proporciona mensajes claros.
* No incluyas secretos ni rutas hardcodeadas; usa variables de
  entorno o un archivo de configuración en `configs/`.

## Pruebas

* Añade pruebas unitarias para cualquier función o módulo nuevo.
* Las pruebas se encuentran en `tests/` y utilizan **pytest**.
* Los scrapers deben tener pruebas de humo (`@pytest.mark.smoke`) que
  verifiquen que pueden arrancar sin red ni credenciales.
* Ejecuta `make test` para asegurarte de que todas las pruebas
  existentes siguen pasando.

## Convención de ramas y commits

* Usa prefijos claros para las ramas: `feature/`, `fix/`,
  `chore/`, `docs/` según corresponda.
* Los mensajes de commit deben ser breves y en imperativo: “Añade
  test para limpiar_df” en lugar de “Añadido...”.
* Realiza commits atómicos; evita mezclar refactorizaciones con
  cambios funcionales en un mismo commit.

## Pull requests

Cuando abras un pull request:

* Asegúrate de rellenar todos los campos de la plantilla
  `.github/PULL_REQUEST_TEMPLATE.md`.
* Describe qué problema resuelve o qué funcionalidad añade tu cambio.
* Incluye cualquier instrucción especial para probar o reproducir.
* Marca en la checklist si has actualizado el README o la documentación.

## Código de conducta

Pedimos a todos los colaboradores que respeten un trato cordial y
constructivo.  Cualquier comportamiento abusivo o discriminatorio no
será tolerado.

## Licencia

Al contribuir confirmas que tu código se publica bajo la licencia MIT
de este proyecto.