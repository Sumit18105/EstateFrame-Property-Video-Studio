# EstateFrame — Property Film Studio

EstateFrame is a Python + Streamlit application that converts a property's verified details and 4–8 photographs into a shareable MP4. It uses a focused luxury interface with a warm brown / burgundy palette, one horizontal navigation bar, and a four-step workflow.

## Run on Windows

1. Extract this project folder.
2. Open Command Prompt in `EstateFrame_Studio`.
3. Install the dependencies and start this version on port 8505 (so an older running copy cannot be confused with it):

```cmd
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.port 8505
```

Open `http://localhost:8505`. You can alternatively double-click `run_app.bat` after installing dependencies.

## Workflow

1. Enter the property name, location, type, price, optional room/area facts, description, verified features, enquiry text, and optional branding.
2. Upload 4–8 JPG/JPEG/PNG images (10 MB max each). Remove and reorder photos, and edit each scene caption.
3. Select a visual style and output format (16:9, 9:16, or 1:1). Review and edit the template-generated narration script. Narration and music are optional.
4. Generate the MP4, preview it in the app, and download the actual exported file.

## Project structure

- `app.py` — page routing, state management, validation, upload flow, and MP4 export.
- `styles.py` — custom responsive UI and dark luxury theme.
- `components.py` — the cover preview and workflow stepper.
- `script_engine.py` — factual, template-based narration and scene planning.
- `video_engine.py` — animated scenes, overlays, crossfade transitions, optional audio, and MP4 encoding via `imageio-ffmpeg`.
- `assets/demo/` — AI-generated sample property visuals for the fictional listing.
- `sample_property.json` — clearly fictional example data.
- `sample_output/` — sample MP4 and preview images.
- `tests/` — automated tests for script content and MP4 rendering.

## Models, libraries, and limitations

- **Script and captions:** deterministic template logic; no external LLM API is configured. Text is assembled only from details and captions supplied in the form.
- **Narration:** optional English text-to-speech through `gTTS`; it needs internet access. If it fails, video export can continue without narration and the app reports the audio status.
- **Video:** Pillow + NumPy create animated image scenes and text overlays; `imageio-ffmpeg` encodes H.264 MP4. Crossfades are included between scenes.
- **Background music:** optional user-provided audio file. Only use music you have permission to publish.
- **History:** session-scoped; it does not persist after the Streamlit session ends.
- **Demo photos and listing:** generated / synthetic sample data. Replace them with authorized property photographs and verified facts before publishing.

The renderer validates that there are 4–8 valid images and handles missing optional values by omitting them from the copy. Generated videos are written to `outputs/`; output resolution is 1280×720 (16:9), 720×1280 (9:16), or 1080×1080 (1:1). The bundled sample MP4 is rendered at a smaller resolution to keep the project download compact.
