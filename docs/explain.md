# Regex

Se usará para el punto de **post preprocessing**

Buscaremos lo siguiente:

- Menciones @
- hashtags #
- links https://
- emojis ¿

Deberemos normalizar el texto, colocándolo en minúsculas y quitando espacios extra.

### ¿Cómo?

Busco dado una cadena de texto las meciones mediante `@’s` , los hashtags con `#'s` , …

**Dependecias**

```java
import re
```

**Texto normalizado**

se evalúa todo el texto antes de ejecutarse el programa y buscamos que este quede en minúsculas y sin espacios innecesarios los cuales puedan interferir en la ejecución de las expresiones regulares