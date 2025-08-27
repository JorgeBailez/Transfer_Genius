# Diccionario de Datos

Este documento describe las columnas presentes en el dataset
longitudinal generado a partir de la unión de FBref y Transfermarkt.
Las tablas intermedias pueden contener subconjuntos de estas
columnas.  Para cada atributo se especifica su tipo, dominio y
comentarios relevantes.

| Columna            | Tipo     | Dominio / Descripción                                   |
|--------------------|----------|--------------------------------------------------------|
| **player**         | string   | Nombre completo del jugador.                          |
| **position**       | string   | Posición en el campo (e.g. `CF`, `GK`, `CB`).          |
| **age**            | integer  | Edad en años del jugador.                              |
| **market_value**   | string   | Valor de mercado según Transfermarkt (ej. `€10m`).     |
| **mv_millions**    | float    | Valor de mercado expresado en millones de euros.        |
| **club**           | string   | Club al que pertenece el jugador en la temporada dada. |
| **nationality**    | list     | Lista de nacionalidades del jugador (códigos FIFA).    |
| **player_url**     | string   | URL absoluta a la ficha del jugador en Transfermarkt.  |
| **Nation**         | string   | Código de país normalizado procedente de FBref.        |
| **Season**         | string   | Temporada en formato `YYYY/YYYY` (p.ej. `2019/2020`).   |
| **Team**           | string   | Equipo en FBref (puede diferir de `club`).             |
| **Player_norm**    | string   | Nombre del jugador normalizado y sin acentos.          |
| **player_norm**    | string   | Nombre del jugador normalizado (Transfermarkt).        |

Otros campos presentes en los ficheros originales de FBref se
conservan cuando son pertinentes (minutos jugados, goles, asistencias,
etc.).  Las columnas auxiliares `Player_norm` y `player_norm` se
utilizan únicamente para la correspondencia entre tablas y se pueden
descartar en análisis posteriores.