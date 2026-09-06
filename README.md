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

---

<h2 align="center">DESCARGA</h2>

<p align="center">
  <a href="https://github.com/OyasumiDev/PROJECT-4414-ASCII-INTERFACE/releases/latest/download/PROJECT-4414.exe">
    <img src="https://img.shields.io/github/v/release/OyasumiDev/PROJECT-4414-ASCII-INTERFACE?label=Download%20for%20Windows&logo=windows&logoColor=white&style=for-the-badge&color=0078D4" alt="Download for Windows" height="48">
  </a>
</p>

<p align="center">
  <a href="https://github.com/OyasumiDev/PROJECT-4414-ASCII-INTERFACE/releases/latest">
    <img src="https://img.shields.io/github/downloads/OyasumiDev/PROJECT-4414-ASCII-INTERFACE/total?style=flat-square&color=555&label=total%20downloads" alt="Total downloads">
  </a>
  &nbsp;
  <img src="https://img.shields.io/badge/platform-Windows%2010%2F11%20%C2%B7%2064--bit-0078D4?style=flat-square&logo=windows&logoColor=white" alt="Windows 10/11 64-bit">
  &nbsp;
  <img src="https://img.shields.io/badge/no%20install%20required-just%20run%20the%20.exe-brightgreen?style=flat-square" alt="No install required">
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
| **Pantalla → ASCII en vivo** | Captura el escritorio (monitor completo, monitor concreto, todos los monitores o una región `x/y/w/h`) con `mss` y lo pasa por el mismo pipeline. Selector **Cámara / Pantalla** en la UI + control de **Calidad** (100/75/50/33 %) para bajar el coste a alta resolución |
| **Modo color** | Cada carácter toma el color RGB real del píxel correspondiente |
| **5 paletas de caracteres** | `SIMPLE` · `BLOCKS` · `DENSE` · `BRAILLE` · `CUSTOM` |
| **Control de parámetros en vivo** | Columnas (20–500), Brillo (curva gamma), FPS, tamaño de fuente y resolución ajustables sin reiniciar |
| **Pipeline optimizado** | Una sola operación a resolución completa por frame; rasterizado ASCII por atlas de glifos vectorizado (sin `draw.text` por carácter); PNG rápido con lienzo acotado |
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
| [`mss`](https://pypi.org/project/mss/) | ≥ 9.0.1 | Captura rápida de pantalla de escritorio (fuente "Pantalla") |
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
    │   ├── app_state.py           # Singleton — estado global (fuente activa + params)
    │   ├── abstracts/
    │   │   └── base_converter.py  # ABC para conversores frame → ASCII
    │   ├── interfaces/
    │   │   ├── i_converter.py     # Protocol estructural para conversores
    │   │   ├── i_frame_source.py  # Protocol común a CameraWorker / ScreenWorker
    │   │   └── i_observer.py      # Protocols IObserver / IObservable
    │   ├── patterns/
    │   │   ├── singleton.py       # Metaclase SingletonMeta
    │   │   └── observable.py      # Implementación genérica del patrón Observer
    │   └── state/
    │       └── camera_state.py    # Gestor de transiciones de estado de la captura
    │
    ├── controllers/
    │   ├── capture_controller.py  # Orquesta el worker de cámara O pantalla según SourceType
    │   ├── camera_controller.py   # (legacy) orquestador sólo-cámara, se mantiene por compat
    │   └── params_controller.py   # Aplica cambios de parámetros en tiempo real
    │
    ├── enums/
    │   ├── e_camera_state.py      # Enum: IDLE / RUNNING / PAUSED / ERROR
    │   ├── e_source_type.py       # Enum: CAMERA / SCREEN
    │   └── e_charset.py           # Enum: SIMPLE / BLOCKS / DENSE / BRAILLE / CUSTOM
    │
    ├── helpers/
    │   ├── validators.py          # Validación de entradas sin excepciones
    │   ├── ascii/
    │   │   ├── ascii_converter.py # pixel → índice de carácter (numpy); grid sin strings
    │   │   ├── ascii_renderer.py  # Renderiza ASCII a PNG base64 (PIL)
    │   │   └── ascii_color_helper.py  # Extrae color promedio por bloque de píxeles
    │   ├── capture/
    │   │   └── base_capture_worker.py # Thread daemon base: lifecycle, throttle, lag, reconexión, pipeline
    │   ├── camera/
    │   │   ├── camera_worker.py       # Hooks de captura webcam (cv2) sobre BaseCaptureWorker
    │   │   ├── camera_enumerator.py   # Detecta cámaras disponibles (PnP + cv2)
    │   │   └── frame_preprocessor.py  # BGR→gris, CLAHE (objeto cacheado), brillo gamma (LUT)
    │   └── screen/
    │       ├── screen_worker.py       # Hooks de captura de pantalla (mss) sobre BaseCaptureWorker
    │       └── screen_enumerator.py   # Lista monitores vía mss.monitors
    │
    ├── models/
    │   ├── ascii_params_model.py     # Dataclass con todos los parámetros de conversión
    │   ├── ascii_frame_model.py      # Dataclass con el resultado de un frame procesado
    │   └── capture_request_model.py  # Dataclass: fuente + params (UI → CaptureController)
    │
    └── views/
        ├── main_window.py         # Ventana principal + _FrameBridge thread-safe
        └── components/
            ├── controls_widget.py # Panel: selector Cámara/Pantalla + monitor/región + Start/Stop/Pause
            ├── region_dialog.py   # Diálogo x/y/w/h para definir una región de pantalla
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
    ├── CaptureController         Instancia el worker correcto según SourceType
    │   │                         y respeta el lifecycle start/stop/pause/resume
    │   └── BaseCaptureWorker     Thread daemon: throttle FPS, detección de lag,
    │       │                     reconexión y pipeline ASCII compartido
    │       ├── CameraWorker      hooks: cv2.VideoCapture (DSHOW→MSMF, MJPG)
    │       │                     └── satisface IFrameSource
    │       ├── ScreenWorker      hooks: mss (monitor / región, reescala por Calidad)
    │       │                     └── satisface IFrameSource
    │       ├── cv2.resize            frame completo → rejilla (cols × rows)  ← única op a full-res
    │       ├── FramePreprocessor     brillo gamma (LUT) → gris → CLAHE  (sobre la rejilla)
    │       ├── AsciiConverter        numpy: intensidad → grid de índices
    │       └── AsciiRenderer         atlas de glifos → PNG base64 (lienzo ≤ 1600px)
    │
    ├── ParamsController          Modifica AsciiParams en tiempo real (sin reiniciar)
    │
    └── AppState (Singleton)      Estado global compartido entre controllers y worker
        ├── AsciiParams           cols, brightness, fps, charset, color_mode, resolution…
        ├── SourceType            CAMERA / SCREEN  (+ cam_index / monitor / región / calidad)
        └── CameraState           IDLE / RUNNING / PAUSED / ERROR
```

**Flujo de un frame:**

```
[ Webcam  → cap.read()          ]
[ Pantalla → mss.grab() → BGRA→BGR (+ reescala por Calidad) ]
        → cv2.resize a la rejilla (cols × rows)        ← única op a resolución completa
        → apply_brightness (gamma) → gris → CLAHE       (sobre la rejilla, coste marginal)
        → AsciiConverter.to_index_grid  (numpy → grid de índices)
        → AsciiRenderer.render_grid_to_base64  (atlas de glifos → PNG, lienzo ≤ 1600px)
        → AsciiFrame(image_b64) → _FrameBridge.on_frame()
        → pyqtSignal → AsciiDisplayWidget.set_frame() → QLabel (pantalla)
```

El pipeline y todos los parámetros (`cols`, `fps`, `charset`, `invert`,
`color_mode`, `brightness`) son idénticos para ambas fuentes: sólo cambia de
dónde sale el `numpy` BGR. El *throttle* duerme lo que falte para el periodo del
FPS pedido (nunca hace busy-loop), de modo que el FPS actúa de tope real y la CPU
descansa entre frames.

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

**`app_state.py`** — `AppState` es el Singleton central de la aplicación. Contiene `params` (AsciiParams), `camera_state` (CameraState), `source_type` (SourceType) y los parámetros de cada fuente (`current_cam_index`, `current_monitor_index`, `screen_region`, `screen_quality`). Es el único punto de verdad compartido; cualquier módulo que llame `AppState()` obtiene exactamente la misma instancia.

**`abstracts/base_converter.py`** — Clase abstracta (ABC) `BaseConverter`. Define el contrato que deben cumplir todos los conversores mediante el método abstracto `convert(frame, cols, invert, charset)`.

**`interfaces/i_converter.py`** — `IConverter`: Protocol estructural para conversores (PEP 544). No requiere herencia; cualquier clase que implemente `convert()` satisface la interfaz por duck-typing.

**`interfaces/i_frame_source.py`** — `IFrameSource`: Protocol estructural que define el ciclo de vida común a toda fuente de frames (`start` / `stop` / `pause` / `resume` / `is_alive`) y el contrato de callbacks `on_frame` / `on_status`. Lo satisfacen `CameraWorker` y `ScreenWorker` (ambos vía `BaseCaptureWorker`).

**`interfaces/i_observer.py`** — `IObserver` / `IObservable`: Protocolos para el patrón Observer. `IObserver` exige `update(data)`, `IObservable` exige `subscribe()` y `notify()`.

**`patterns/singleton.py`** — `SingletonMeta`: metaclase que garantiza una sola instancia por clase durante toda la vida del proceso.

**`patterns/observable.py`** — `Observable`: implementación genérica del patrón Observer con `subscribe()`, `unsubscribe()` y `notify()`.

**`state/camera_state.py`** — `CameraStateManager`: encapsula el `CameraState` actual y gestiona las transiciones `IDLE → RUNNING → PAUSED → ERROR`.

---

### `app/controllers/`

**`capture_controller.py`** — `CaptureController`: orquestador único de la captura. `start(CaptureRequest)` mira el `SourceType` e instancia `CameraWorker` o `ScreenWorker` (ambos con idéntico lifecycle por derivar de `BaseCaptureWorker`). Guarda la fuente activa y sus parámetros en `AppState`. Al iniciar hace `join(timeout=10s)` al worker anterior. `stop()` / `pause()` / `resume()` iguales que antes.

**`camera_controller.py`** — `CameraController` (legacy): orquestador sólo-cámara previo a la generalización. Se conserva intacto por compatibilidad; la app usa `CaptureController`.

**`params_controller.py`** — `ParamsController`: aplica cambios de parámetros en tiempo real sin reiniciar la cámara. Métodos: `set_cols` (20–500), `set_brightness` (50–220), `set_fps`, `set_font_size`, `set_invert`, `set_charset`, `set_color_mode`, `set_resolution`. Los valores se sanitizan (clamp) antes de escribirse en `AppState`.

---

### `app/enums/`

**`e_camera_state.py`** — `CameraState`: enum con los 4 estados del ciclo de vida de la captura: `IDLE`, `RUNNING`, `PAUSED`, `ERROR`.

**`e_source_type.py`** — `SourceType`: enum de la fuente de frames activa: `CAMERA` (webcam vía cv2) / `SCREEN` (escritorio vía mss).

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

**`ascii_converter.py`** — `AsciiConverter`: mapeo intensidad → carácter, todo con numpy. `to_index_grid(gray_small, invert, charset)` (ruta rápida del worker) recibe el gris ya reducido a la rejilla y devuelve el **grid de índices** (uint8) + la paleta, sin construir strings. `convert(...)` se mantiene como compat y devuelve el string ASCII. `rows_for()` corrige el aspect ratio con factor `0.43` (los chars de terminal son ~2× más altos que anchos).

**`ascii_renderer.py`** — `AsciiRenderer`: rasteriza la rejilla a PNG base64 por **atlas de glifos vectorizado**. `render_grid_to_base64(grid, chars, params, color_cells=…)` es la ruta rápida (recibe el grid de índices, sin parsear strings); `render_to_base64(ascii_str, …)` queda como compat. Cada carácter se dibuja una vez a una celda `char_w×char_h` (atlas cacheado por `font_size`+charset); cada frame la máscara de tinta completa es `atlas[grid]` + `reshape`. Modo grises con colores por defecto → la máscara **es** la imagen (mode `L`); modo color → `cv2.multiply(color_layer, máscara)` (SIMD). El PNG se guarda con `compress_level=1` y el lienzo se limita a `_MAX_OUT_W` (1600 px) con un único `cv2.resize`. Fallback a `draw.text` si el atlas fallara.

**`ascii_color_helper.py`** — `AsciiColorHelper`: divide el frame BGR en una grilla de bloques y extrae el color promedio (mean de `axis=(0,1)`) de cada uno. Devuelve una grilla `[rows][cols]` de tuplas RGB, usada para el modo color del renderer.

---

### `app/helpers/capture/`

**`base_capture_worker.py`** — `BaseCaptureWorker(threading.Thread)`: clase base con **toda** la lógica común a cualquier fuente, que antes vivía sólo en `CameraWorker`: ciclo de vida `run/stop/pause/resume` con `_stop_event`, lectura thread-safe de `AsciiParams` bajo lock, throttle de FPS con `effective_interval`, detección de lag por ventana deslizante, reconexión genérica (N fallos → cerrar/reabrir, hasta M veces) y el pipeline ASCII compartido. Las subclases sólo implementan los hooks `_setup()`, `_read_frame()`, `_apply_params()`, `_teardown()` y opcionalmente los mensajes `_msg_*`.

---

### `app/helpers/camera/`

**`camera_worker.py`** — `CameraWorker(BaseCaptureWorker)`: implementa los hooks para `cv2.VideoCapture`. Apertura con timeout por intento (DSHOW → MSMF como fallback), descarte del handle fantasma `0×0`, negociación de formato MJPG y resolución en el orden correcto para DSHOW, y cambio de resolución en caliente vía `_apply_params()`. El comportamiento de apertura y los mensajes se conservan idénticos a la versión previa.

**`camera_enumerator.py`** — Dos funciones: `list_cameras_fast()` consulta el PnP de Windows vía PowerShell sin abrir cámaras (usado al arrancar), y `enumerate_cameras()` hace un scan completo abriendo cada índice con `cv2` (para el botón Refresh).

**`frame_preprocessor.py`** — `FramePreprocessor`: `to_gray()` BGR→gris; `normalize()` aplica CLAHE (`clipLimit=2.0`, objeto **creado una sola vez** y reutilizado); `apply_brightness(frame, brightness)` aplica una curva **gamma** vía LUT cacheada (`cv2.LUT`, SIMD; `100` = identidad); `flip_horizontal()` modo espejo. En el pipeline nuevo estas ops corren sobre la rejilla (cols×rows), así que su coste es marginal.

---

### `app/helpers/screen/`

**`screen_worker.py`** — `ScreenWorker(BaseCaptureWorker)`: implementa los hooks sobre `mss`. Captura un monitor (`mss.monitors[i]`, con `0` = todos los monitores) o una región `(x, y, w, h)` del escritorio virtual; convierte BGRA→BGR y aplica un reescalado por el factor **Calidad** (0.1–1.0) más un downscale de seguridad si el ancho supera 1920 px. El objeto `mss` se crea dentro de `_setup()` porque no es thread-safe y debe vivir en el hilo del worker.

**`screen_enumerator.py`** — `list_monitors()`: devuelve `[(mss_index, etiqueta)]` a partir de `mss.mss().monitors`. Ofrece "Todos los monitores" sólo cuando hay 2+ físicos. Nunca lanza: ante cualquier fallo devuelve un monitor principal ficticio.

---

### `app/helpers/validators.py`
Funciones de validación de entradas sin excepciones. `validate_cam_index()` (rango 0–10) y `validate_cols()` (rango 20–500). Ante cualquier valor inválido devuelven un default seguro.

---

### `app/models/`

**`ascii_params_model.py`** — `AsciiParams`: dataclass con todos los parámetros configurables de la conversión: `cols` (100), `brightness` (115), `fps` (15), `font_size` (8), `invert` (False), `charset` ("SIMPLE"), `color_mode` (False), `resolution` (640×480). Los defaults se leen de `config.py` (`DEFAULT_BRIGHTNESS` incluido).

**`ascii_frame_model.py`** — `AsciiFrame`: dataclass que representa el resultado de un frame procesado. Contiene `ascii_str` (el texto), `image_b64` (el PNG renderizado en base64), `width`, `height` y `timestamp`.

**`capture_request_model.py`** — `CaptureRequest`: dataclass que viaja de la UI a `CaptureController.start()`. Agrupa `source_type` (`SourceType`), `cam_index`, `monitor_index`, `region` y `quality`.

---

### `app/views/`

**`main_window.py`** — `MainWindow`: ventana principal. Construye el layout (display a la izquierda, sidebar scrollable a la derecha de 290px). Contiene `_FrameBridge`, un `QObject` con `pyqtSignal` que actúa como puente thread-safe entre los callbacks del worker y los slots Qt del hilo principal. Aplica el stylesheet global dark (`_STYLE`).

**`components/controls_widget.py`** — `CameraControlsWidget`: panel lateral de controles. Radio **Cámara / Pantalla** que alterna un `QStackedWidget`: página cámara (combo de dispositivos + Refresh) y página pantalla (combo de monitores + Calidad 100/75/50/33 % + botón "Seleccionar región…"). Botones Start/Stop/Pause/Resume y etiqueta de estado con color según nivel (info `#888` / warn `#ffb300` / error `#ef5350` / run `#4caf50`). `start_requested` emite un `CaptureRequest`; `MainWindow` lo conecta a `CaptureController`.

**`components/region_dialog.py`** — `RegionDialog`: diálogo modal con 4 `QSpinBox` (`x`, `y`, ancho, alto) acotados a la geometría del escritorio virtual, más un botón "Usar pantalla completa". Se optó por entrada numérica en lugar de un selector visual arrastrable por simplicidad y robustez.

**`components/display_widget.py`** — `AsciiDisplayWidget`: `QLabel` que recibe el PNG en base64, lo decodifica a `QPixmap` y lo escala manteniendo aspect ratio con `SmoothTransformation` en cada `resizeEvent`.

**`components/params_widget.py`** — `ParamsWidget`: panel lateral de parámetros. Sliders con etiqueta de valor en vivo (Columnas 20–500, **Brillo** 50–220, FPS, Tamaño fuente), combos de Charset y Resolución (480p / 720p / 1080p), y checkboxes de Invertir y Modo color. Todos los cambios llaman a `ParamsController` en tiempo real sin reiniciar la captura.

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
