# Despliegue automático de la demo en Netlify

**Objetivo**: eliminar el ZIP manual. Cada `git push` publica la demo automáticamente
(~1 minuto), sin problemas de caché.

## Configuración inicial (una sola vez, ~15 min)

1. **Crear el repositorio remoto privado** en GitHub (o Azure DevOps, dado el M365 del grupo):
   - GitHub → New repository → `agora-aspanias` → **Private**.
   - No inicializar con README (el repo local ya tiene historia).

2. **Conectar el repo local** (desde la carpeta del proyecto):
   ```
   git remote add origin https://github.com/<organizacion>/agora-aspanias.git
   git push -u origin main
   ```

3. **Conectar Netlify al repo**:
   - Netlify → *Add new site* → *Import an existing project* → GitHub → `agora-aspanias`.
   - Netlify lee `netlify.toml` automáticamente (publish `demo/`, build `npm ci && npm run build:css`).
   - Deploy. A partir de aquí, **cada push a `main` publica solo**.

4. **Proteger la demo** (datos sintéticos, pero es un prototipo interno):
   - Netlify → Site configuration → *Visitor access* → Password protection (plan Pro)
     o al menos mantener la URL sin difundir + `robots.txt` (ya incluido en `demo/`).

## Flujo de trabajo desde entonces

```
(editar demo) → python scripts/utilidades/build_demo.py
             → python scripts/utilidades/check_gobernanza.py
             → git add -A && git commit -m "feat: ..."
             → git push        ← esto publica
```

El paso de Tailwind ya no es necesario en local para publicar (lo hace Netlify),
aunque sigue siendo útil para previsualizar (`npm run build:css`).

## Mientras no exista el remoto

El método ZIP sigue funcionando: `dist/actual/AGORA-demo-para-netlify.zip` → arrastrar
a Netlify. El ZIP ya incluye `tailwind.css` generado en local.
