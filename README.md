# Rey Roller's — sitio + panel de edición

Sitio estático para Netlify. El cliente edita fotos y textos de productos desde `/admin` (Decap CMS); cada cambio se guarda en este repo y Netlify republica solo.

## Estructura
- `site/` — lo que se publica (HTML generado, CSS, JS, imágenes, `admin/`).
- `work/build.py` + `work/templates/` + `work/data/products/` — generador. **Los textos y fotos de cada producto viven en `work/data/products/<slug>.json`** (un archivo por producto; es lo que edita el panel).
- `site/uploads/` — fotos originales subidas desde el panel. El build las optimiza a `site/assets/img/products/`.
- `netlify.toml` — comando de build (`python3 work/build.py`), cabeceras y caché.

## Puesta en marcha (una sola vez)
1. Crear un repo en GitHub y subir esta carpeta completa. **Ojo con Netlify (plan gratis):** en un repo privado solo permite UN colaborador; si el cliente publica desde el panel, Netlify bloquea el deploy ("Unrecognized Git contributor"). Soluciones: repo público, publicar con GitHub Actions o plan Pro.
2. En Netlify: *Add new site → Import from Git*, elegir el repo. El build y la carpeta de publicación ya vienen en `netlify.toml`.
3. En GitHub: *Settings → Developer settings → OAuth Apps → New*. Homepage = URL del sitio; callback = `https://api.netlify.com/auth/done`. Copiar Client ID y generar Client Secret.
4. En Netlify: *Site configuration → Access & security → OAuth → Install provider → GitHub*, pegar Client ID y Secret.
5. Editar `site/admin/config.yml`: cambiar `repo: TU-USUARIO/rey-rollers` por el repo real.
6. En GitHub: *Settings → Collaborators* → invitar al cliente (necesita cuenta gratuita de GitHub y aceptar la invitación).

## Uso del cliente
Entrar a `https://TU-SITIO/admin` → "Iniciar sesión con GitHub" → *Productos y fotos* → abrir un producto → arrastrar fotos / editar texto → **Publicar**. En 1–2 minutos el sitio se actualiza.
La primera foto de la lista es la que aparece en la tarjeta del producto.

## Notas
- El cliente no puede agregar ni borrar productos (solo editar los existentes). Para agregar uno, se crea un nuevo archivo en `work/data/products/` (copiando uno existente y cambiando `slug` y `order`).
- Quien no sea colaborador del repo puede ver la pantalla de login pero GitHub no le deja guardar nada.
- `site/admin/decap-cms*.js` es Decap CMS 3.17.3 alojado en el propio sitio (sin CDN).
- Build local: `pip install Pillow && python3 work/build.py`.
