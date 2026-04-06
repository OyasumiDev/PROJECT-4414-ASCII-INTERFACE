<h1 align="center">PROJECT 4414 — ASCII INTERFACE</h1>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11%2B-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PyQt6-6.11%2B-41CD52?logo=qt&logoColor=white" alt="PyQt6">
  <img src="https://img.shields.io/badge/OpenCV-4.13%2B-5C3EE8?logo=opencv&logoColor=white" alt="OpenCV">
  <img src="https://img.shields.io/badge/Pillow-12.2%2B-green?logo=python&logoColor=white" alt="Pillow">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-555?logo=github&logoColor=white" alt="Platform">
  <img src="https://img.shields.io/badge/status-ACTIVE-brightgreen" alt="Status">
  <img src="https://img.shields.io/badge/project-4414-blueviolet" alt="Repo">
  <img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="License">
</p>

<h2 align="center">⬇️ Download / Descargar</h2>

<p align="center">
  <a href="https://github.com/OyasumiDev/PROJECT-4414-ASCII-INTERFACE/releases/latest" target="_blank" rel="noopener noreferrer">
    <img src="https://img.shields.io/github/v/release/OyasumiDev/PROJECT-4414-ASCII-INTERFACE?label=Latest%20Release&logo=github&style=for-the-badge&color=blueviolet" alt="Latest Release" height="40">
  </a>
</p>

<p align="center">
  <b>🇬🇧 No Python required — just download and run the <code>.exe</code></b><br>
  <b>🇪🇸 Sin necesidad de Python — descarga y ejecuta el <code>.exe</code> directamente</b>
</p>

---

<h1 align="center">MIS REDES</h1>

<p align="center">
  <a href="https://github.com/OyasumiDev" target="_blank" rel="noopener noreferrer">
    <img src="https://img.shields.io/badge/GitHub-OyasumiDev-181717?logo=github&logoColor=white&style=for-the-badge" alt="GitHub" height="40">
  </a>
  &nbsp;&nbsp;
  <a href="https://www.tiktok.com/@oyasumi_dev" target="_blank" rel="noopener noreferrer">
    <img src="https://img.shields.io/badge/TikTok-@oyasumi__dev-000000?logo=tiktok&logoColor=white&style=for-the-badge" alt="TikTok" height="40">
  </a>
</p>

<p align="center">
  <img src="assets/icons/ROJECT%204414%20%E2%80%94%20ASCII%20GALAXY%20GIF.gif" alt="NGC 4414 ASCII art" width="820">
</p>

<p align="center">
  Aplicación de escritorio que convierte el feed de tu webcam en arte ASCII en tiempo real.<br>
  Inspirada en <strong>NGC 4414</strong> — galaxia espiral floculenta en Coma Berenices,<br>
  a 62 millones de años luz. Fotografiada por el Hubble Space Telescope en 1995.<br>
  Descubierta por William Herschel el 13 de marzo de 1785.
</p>

---

## Preview

<p align="center">
  <img src="assets/icons/ROJECT%204414%20%E2%80%94%20EXECUTION%20PREVIEW.png" alt="ASCII Cam screenshot" width="900">
</p>

---

## Features

| Feature | Detalle |
|---|---|
| **Webcam → ASCII en vivo** | Convierte el feed de la cámara a arte ASCII frame a frame en tiempo real |
| **Modo color** | Cada carácter toma el color RGB real del píxel correspondiente |
| **5 paletas de caracteres** | `SIMPLE` · `BLOCKS` · `DENSE` · `BRAILLE` · `CUSTOM` |
| **Control de parámetros en vivo** | Columnas, FPS, tamaño de fuente y resolución ajustables sin reiniciar |
| **Inversión de paleta** | Útil para cámaras o ambientes con fondo claro |
| **Multi-cámara** | Detección automática de dispositivos con nombres reales (vía PnP en Windows) |
| **Reconexión automática** | El worker reintenta la conexión si el stream se corta |
| **Detección de lag** | Avisa si la cámara está sobrecargada y sugiere bajar parámetros |
| **UI dark mode** | Interfaz minimalista con sidebar scrollable y theme oscuro (Fusion + QSS) |

---

## Installation

```bash
# 1. Clonar el repositorio
git clone https://github.com/OyasumiDev/project-4414.git
cd project-4414

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar
python main.py
```

### Dependencias

| Package | Version | Propósito |
|---|---|---|
| [`PyQt6`](https://pypi.org/project/PyQt6/) | ≥ 6.11.0 | GUI — ventana, widgets, event loop, señales Qt |
| [`opencv-python`](https://pypi.org/project/opencv-python/) | ≥ 4.13.0 | Captura de webcam, resize, conversión de color, CLAHE |
| [`numpy`](https://pypi.org/project/numpy/) | ≥ 2.4.0 | Mapeo vectorizado pixel → carácter ASCII |
| [`Pillow`](https://pypi.org/project/Pillow/) | ≥ 12.2.0 | Renderizado del ASCII a imagen PNG con fuente monoespaciada |
| [`python-dotenv`](https://pypi.org/project/python-dotenv/) | ≥ 1.2.0 | Carga de configuración desde `.env` |

---

## Project Structure

```
Ascii_project/
│
├── main.py                        # Punto de entrada — QApplication + MainWindow
├── Ascii_folder.py                # Utilitario auxiliar (procesado por lotes)
├── requirements.txt
├── README.md
│
├── assets/
│   └── icons/
│       ├── ROJECT 4414 — ASCII Galaxy ICON.ico    # Ícono de la app (Windows taskbar)
│       ├── ROJECT 4414 — ASCII GALAXY GIF.gif     # Preview animado del README
│       └── ROJECT 4414 — EXECUTION PREVIEW.png   # Captura de pantalla del README
│
└── app/
    │
    ├── config/
    │   ├── config.py              # Constantes globales desde .env
    │   └── settings.py            # Ajustes persistentes (tema, última cámara)
    │
    ├── core/
    │   ├── app_state.py           # Singleton — estado global de la app
    │   ├── abstracts/
    │   │   └── base_converter.py  # ABC para conversores frame → ASCII
    │   ├── interfaces/
    │   │   ├── i_converter.py     # Protocol estructural para conversores
    │   │   └── i_observer.py      # Protocols IObserver / IObservable
    │   ├── patterns/
    │   │   ├── singleton.py       # Metaclase SingletonMeta
    │   │   └── observable.py      # Implementación genérica del patrón Observer
    │   └── state/
    │       └── camera_state.py    # Gestor de transiciones de estado de la cámara
    │
    ├── controllers/
    │   ├── camera_controller.py   # Orquesta el ciclo de vida del CameraWorker
    │   └── params_controller.py   # Aplica cambios de parámetros en tiempo real
    │
    ├── enums/
    │   ├── e_camera_state.py      # Enum: IDLE / RUNNING / PAUSED / ERROR
    │   └── e_charset.py           # Enum: SIMPLE / BLOCKS / DENSE / BRAILLE / CUSTOM
    │
    ├── helpers/
    │   ├── validators.py          # Validación de entradas sin excepciones
    │   ├── ascii/
    │   │   ├── ascii_converter.py # Algoritmo principal pixel → char (numpy)
    │   │   ├── ascii_renderer.py  # Renderiza ASCII a PNG base64 (PIL)
    │   │   └── ascii_color_helper.py  # Extrae color promedio por bloque de píxeles
    │   └── camera/
    │       ├── camera_worker.py       # Thread daemon de captura y procesado
    │       ├── camera_enumerator.py   # Detecta cámaras disponibles (PnP + cv2)
    │       └── frame_preprocessor.py  # BGR→gris, CLAHE, flip horizontal
    │
    ├── models/
    │   ├── ascii_params_model.py  # Dataclass con todos los parámetros de conversión
    │   └── ascii_frame_model.py   # Dataclass con el resultado de un frame procesado
    │
    └── views/
        ├── main_window.py         # Ventana principal + _FrameBridge thread-safe
        └── components/
            ├── controls_widget.py # Panel: selector de cámara + Start/Stop/Pause
            ├── display_widget.py  # Widget que muestra el frame ASCII como imagen
            └── params_widget.py   # Panel: sliders, combos y checkboxes de parámetros
```

---

## Architecture

```
main.py
└── MainWindow (PyQt6)
    │
    ├── _FrameBridge              Puente thread-safe worker → hilo Qt (pyqtSignal)
    │
    ├── CameraController          Orquesta el ciclo de vida del worker
    │   └── CameraWorker          Thread daemon de captura
    │       ├── FramePreprocessor     BGR → gris → CLAHE
    │       ├── AsciiConverter        numpy: pixel → char
    │       └── AsciiRenderer         PIL: string → PNG base64
    │
    ├── ParamsController          Modifica AsciiParams en tiempo real (sin reiniciar)
    │
    └── AppState (Singleton)      Estado global compartido entre controllers y worker
        ├── AsciiParams           cols, fps, charset, color_mode, resolution…
        └── CameraState           IDLE / RUNNING / PAUSED / ERROR
```

**Flujo de un frame:**

```
Webcam → cap.read() → FramePreprocessor → AsciiConverter → AsciiRenderer
→ AsciiFrame(ascii_str, image_b64) → _FrameBridge.on_frame()
→ pyqtSignal → AsciiDisplayWidget.set_frame() → QLabel (pantalla)
```

---

## Modules

### `main.py`
Punto de entrada. Registra el `AppUserModelID` en Windows para que la taskbar muestre el ícono correcto, aplica el estilo Fusion, instancia `MainWindow` y arranca el event loop.

---

### `app/config/`

**`config.py`** — Lee variables desde `.env` con `python-dotenv`. Expone las constantes globales de la app: `CAM_INDEX`, `DEFAULT_COLS`, `DEFAULT_FPS`, `DEFAULT_FONT_SIZE`, `DEFAULT_INVERT`, `DEFAULT_CHARSET`, `APP_TITLE`, `APP_WIDTH`, `APP_HEIGHT`.

**`settings.py`** — Clase `AppSettings` con ajustes persistentes como el tema (`dark`) y la última cámara usada.

---

### `app/core/`

**`app_state.py`** — `AppState` es el Singleton central de la aplicación. Contiene `params` (AsciiParams), `camera_state` (CameraState) y `current_cam_index`. Es el único punto de verdad compartido; cualquier módulo que llame `AppState()` obtiene exactamente la misma instancia.

**`abstracts/base_converter.py`** — Clase abstracta (ABC) `BaseConverter`. Define el contrato que deben cumplir todos los conversores mediante el método abstracto `convert(frame, cols, invert, charset)`.

**`interfaces/i_converter.py`** — `IConverter`: Protocol estructural para conversores (PEP 544). No requiere herencia; cualquier clase que implemente `convert()` satisface la interfaz por duck-typing.

**`interfaces/i_observer.py`** — `IObserver` / `IObservable`: Protocolos para el patrón Observer. `IObserver` exige `update(data)`, `IObservable` exige `subscribe()` y `notify()`.

**`patterns/singleton.py`** — `SingletonMeta`: metaclase que garantiza una sola instancia por clase durante toda la vida del proceso.

**`patterns/observable.py`** — `Observable`: implementación genérica del patrón Observer con `subscribe()`, `unsubscribe()` y `notify()`.

**`state/camera_state.py`** — `CameraStateManager`: encapsula el `CameraState` actual y gestiona las transiciones `IDLE → RUNNING → PAUSED → ERROR`.

---

### `app/controllers/`

**`camera_controller.py`** — `CameraController`: orquesta el ciclo de vida completo del `CameraWorker`. Expone `start(cam_index)`, `stop()`, `pause()` y `resume()`. Sincroniza el `CameraState` en `AppState`. Al iniciar, hace `join(timeout=10s)` al worker anterior para evitar conflictos de acceso al dispositivo.

**`params_controller.py`** — `ParamsController`: aplica cambios de parámetros en tiempo real sin reiniciar la cámara. Métodos: `set_cols`, `set_fps`, `set_font_size`, `set_invert`, `set_charset`, `set_color_mode`, `set_resolution`. Los valores se sanitizan (clamp) antes de escribirse en `AppState`.

---

### `app/enums/`

**`e_camera_state.py`** — `CameraState`: enum con los 4 estados del ciclo de vida de la cámara: `IDLE`, `RUNNING`, `PAUSED`, `ERROR`.

**`e_charset.py`** — `CharSet`: enum con las paletas disponibles:

| Nombre | Caracteres |
|---|---|
| `SIMPLE` | ` .:-=+*#%@` |
| `BLOCKS` | ` ░▒▓█` |
| `DENSE` | 46 caracteres de gradiente fino |
| `BRAILLE` | ` ⠁⠃⠇⠏⠟⠿⣿` |
| `CUSTOM` | String definido por el usuario en la UI |

---

### `app/helpers/ascii/`

**`ascii_converter.py`** — `AsciiConverter`: el algoritmo central. Redimensiona el frame con `cv2.resize(INTER_AREA)`, normaliza el brillo (0–255 → índice de paleta) con numpy y construye el string ASCII multilínea. El aspect ratio se corrige con factor `0.43` (los chars de terminal son ~2× más altos que anchos).

**`ascii_renderer.py`** — `AsciiRenderer`: convierte el string ASCII en una imagen PNG usando PIL `ImageDraw`. Cachea fuentes monoespaciadas. Soporta dos modos: escala de grises (ruta rápida, un solo `draw.text` por línea) y color (samplea el RGB real de cada píxel para colorear cada carácter individualmente). Serializa la imagen a base64 para entregarla al widget Qt.

**`ascii_color_helper.py`** — `AsciiColorHelper`: divide el frame BGR en una grilla de bloques y extrae el color promedio (mean de `axis=(0,1)`) de cada uno. Devuelve una grilla `[rows][cols]` de tuplas RGB, usada para el modo color del renderer.

---

### `app/helpers/camera/`

**`camera_worker.py`** — `CameraWorker`: thread daemon que gestiona el ciclo completo de captura. Apertura con timeout por intento (DSHOW → MSMF como fallback), negociación de formato MJPG, detección de lag por ventana deslizante de 20 frames, reconexión automática hasta 3 veces si el stream se corta, y throttle de FPS con `effective_interval`. Los callbacks `on_frame` / `on_status` no son thread-safe por sí solos; deben pasar por `_FrameBridge`.

**`camera_enumerator.py`** — Dos funciones: `list_cameras_fast()` consulta el PnP de Windows vía PowerShell sin abrir cámaras (usado al arrancar), y `enumerate_cameras()` hace un scan completo abriendo cada índice con `cv2` (para el botón Refresh).

**`frame_preprocessor.py`** — `FramePreprocessor`: preprocesa el frame antes de convertir. `to_gray()` convierte BGR→gris, `normalize()` aplica CLAHE (`clipLimit=2.0`) para mejorar contraste en condiciones de luz variable, y `flip_horizontal()` ofrece modo espejo.

---

### `app/helpers/validators.py`
Funciones de validación de entradas sin excepciones. `validate_cam_index()` (rango 0–10) y `validate_cols()` (rango 20–300). Ante cualquier valor inválido devuelven un default seguro.

---

### `app/models/`

**`ascii_params_model.py`** — `AsciiParams`: dataclass con todos los parámetros configurables de la conversión: `cols` (100), `fps` (15), `font_size` (8), `invert` (False), `charset` ("SIMPLE"), `color_mode` (False), `resolution` (640×480). Los defaults se leen de `config.py`.

**`ascii_frame_model.py`** — `AsciiFrame`: dataclass que representa el resultado de un frame procesado. Contiene `ascii_str` (el texto), `image_b64` (el PNG renderizado en base64), `width`, `height` y `timestamp`.

---

### `app/views/`

**`main_window.py`** — `MainWindow`: ventana principal. Construye el layout (display a la izquierda, sidebar scrollable a la derecha de 290px). Contiene `_FrameBridge`, un `QObject` con `pyqtSignal` que actúa como puente thread-safe entre los callbacks del worker y los slots Qt del hilo principal. Aplica el stylesheet global dark (`_STYLE`).

**`components/controls_widget.py`** — `CameraControlsWidget`: panel lateral de controles. Combo de selección de cámara con nombres reales del dispositivo, botón Refresh que lanza la detección en un hilo de fondo, botones Start/Stop/Pause/Resume, y etiqueta de estado con color según nivel (info `#888` / warn `#ffb300` / error `#ef5350`). Emite señales públicas que `MainWindow` conecta a `CameraController`.

**`components/display_widget.py`** — `AsciiDisplayWidget`: `QLabel` que recibe el PNG en base64, lo decodifica a `QPixmap` y lo escala manteniendo aspect ratio con `SmoothTransformation` en cada `resizeEvent`.

**`components/params_widget.py`** — `ParamsWidget`: panel lateral de parámetros. Sliders con etiqueta de valor en vivo (Columnas, FPS, Tamaño fuente), combos de Charset y Resolución (480p / 720p / 1080p), y checkboxes de Invertir y Modo color. Todos los cambios llaman a `ParamsController` en tiempo real sin reiniciar la cámara.

---

## About NGC 4414

NGC 4414 es una **galaxia espiral floculenta** — un tipo de espiral sin brazos bien definidos, con regiones de formación estelar dispersas como copos. Fue fotografiada por el Hubble en 1995 como parte del *Key Project* para medir la constante de Hubble usando estrellas Cefeidas.

> *"Flocculant"* viene del latín *flocculus* — pequeño copo.

```
DISTANCE      62,000,000 ly    CONSTELLATION   Coma Berenices
DISCOVERED    1785             OBSERVER        William Herschel
IMAGED        1995             INSTRUMENT      Hubble Space Telescope
```

---

---

<p align="center">
  <a href="https://github.com/OyasumiDev" target="_blank" rel="noopener noreferrer">
    <img src="https://img.shields.io/badge/GitHub-OyasumiDev-181717?logo=github&logoColor=white&style=for-the-badge" alt="GitHub">
  </a>
  &nbsp;&nbsp;
  <a href="https://www.tiktok.com/@oyasumi_dev" target="_blank" rel="noopener noreferrer">
    <img src="https://img.shields.io/badge/TikTok-@oyasumi__dev-000000?logo=tiktok&logoColor=white&style=for-the-badge" alt="TikTok">
  </a>
</p>

---

<p align="center">
  <sub>© 2025 Oyasumi Dev · All rights reserved.<br>
  This project and its source code are the exclusive property of their author.<br>
  Unauthorized reproduction, distribution, or use is strictly prohibited.</sub>
</p>
