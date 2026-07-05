# Poster Pic Generator

A small Streamlit app that puts a **real** face from a photo onto a target image (a poster, thumbnail, generated scene -- whatever) using [FaceFusion](https://github.com/facefusion/facefusion).

This is a **real, deterministic face swap** -- it detects the actual face in your source photo and places it onto the target, instead of asking an AI image model to "redraw" a face from a text description (which is how you end up with extra fingers, swapped positions, or a black eye that was actually a peace-sign hand gesture).

## Why this exists

Built after a July 2026 poster job where an AI image generator kept mangling a real photo reference (Higgsfield / Nano Banana) -- swapping which twin was on which side, and misreading a hand gesture near an eye as an injury. FaceFusion actually detects and swaps the real face pixels, so it doesn't hallucinate.

## Two ways to run this

### Option A: Streamlit Community Cloud (what's currently deployed)

If you deployed this repo directly via [share.streamlit.io](https://share.streamlit.io), Streamlit Cloud builds the app automatically from two files in this repo:

- `requirements.txt` -- Python packages, including FaceFusion's own core dependencies (numpy, onnx, onnxruntime, opencv-python-headless, tqdm, scipy) so they're available even though FaceFusion's *code* gets cloned separately at runtime.
- `packages.txt` -- system-level packages (`libgl1`, `libglib2.0-0`) that opencv needs on Streamlit Cloud's minimal Debian image.

On the **first load after a deploy or restart**, expect it to take a few minutes: the app clones FaceFusion's source code into a `facefusion/` folder, and the first face swap you run downloads FaceFusion's model files. Subsequent runs (until the container restarts) are much faster. Free-tier Streamlit Cloud has limited RAM (1 GB) -- if you see the app crash/restart on a swap, it's likely hitting that ceiling.

### Option B: Your own Mac (more headroom, no cold starts)

1. Open **Terminal** on your Mac.
2. Clone this repo and go into it:
   ```
   git clone https://github.com/tocsinrepo/poster-pic-generator.git
   cd poster-pic-generator
   ```
3. (Recommended) Create a virtual environment so this doesn't clash with anything else on your Mac:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```
4. Install the app's own requirements:
   ```
   pip install -r requirements.txt
   ```
5. Launch it:
   ```
   streamlit run app.py
   ```
   Your browser will open automatically to a local page (something like `http://localhost:8501`).
6. **The first time you click "Run Face Swap"**, FaceFusion gets cloned into a `facefusion/` folder and downloads its model files -- this needs real internet access and will **not work inside a network-locked-down sandbox**.
7. If you still see an error mentioning a missing package after that, run:
   ```
   pip install -r facefusion/requirements.txt
   ```
   and try again -- this covers anything FaceFusion added that isn't yet reflected in this repo's own `requirements.txt`.

## How to use it

1. Upload your **source photo** -- the real photo containing the face(s) you want to use.
2. Upload your **target image** -- the poster/scene you want that face placed into.
3. If there are two or more people in the source photo, pick the left-to-right (or other) order so FaceFusion matches faces onto the target in the right order.
4. Click **Run Face Swap**.
5. Download the result.

## Optional: connect your own Higgsfield account (for the animate step)

This repo is **public**, so no one's personal API key is ever written into the code or committed to GitHub. Instead, each person who wants the "animate the result into a video" feature supplies their own Higgsfield credentials locally, in a file that Git is configured to ignore.

**Setup:**

1. Get an API key from [cloud.higgsfield.ai](https://cloud.higgsfield.ai/) (account/API settings).
2. In your local copy of this repo, copy the example env file:
   ```
   cp .env.example .env
   ```
3. Open `.env` in a text editor and paste in your real key (either the single-key format or the key+secret format -- instructions are in the file).
4. Save it. **Do not** rename it to anything else, and never run `git add .env` -- it's already excluded via `.gitignore`, so a normal `git add .` / `git commit` won't pick it up.
5. Restart the app (`streamlit run app.py`). If your key is detected, an "Animate the result" section appears below the face-swap tool after you run a swap.
6. The model ID field is left blank on purpose -- check your [Higgsfield Cloud dashboard](https://cloud.higgsfield.ai/) for the current image-to-video model name and paste it in, since exact model catalog names can change over time.

If you're running this on **Streamlit Community Cloud** instead of locally, set these same variables (`HF_KEY` or `HF_API_KEY`/`HF_API_SECRET`) in the app's **Settings -> Secrets** in the Streamlit Cloud dashboard rather than a local `.env` file -- Streamlit Cloud injects secrets as environment variables the same way.

**Why it's built this way:** if a personal key were hardcoded into `app.py` and pushed to this public repo, anyone browsing GitHub could copy it and spend that person's Higgsfield credits. Keeping it out of the code -- in a local `.env` file or in Streamlit Cloud's Secrets manager -- means the code stays generic and safe to share, while each person's account stays private.

## Turning the finished still into a short video (proven recipe, 2026-07-05)

Once you have a still image you're happy with (face-swapped or not), animating it worked well using **Higgsfield's `kling3_0_turbo` model** with the finished image as the `start_image` reference:

- Model: `kling3_0_turbo`
- Input: the approved still image as `start_image`
- Duration: 5s, 720p was plenty for a personal clip
- Prompt style that worked: describe the action/emotion plainly, e.g. `"The two girls celebrate their birthday together — smiling but not laughing, waving, confetti and fireworks bursting behind them, playful joyful energy, subtle natural movement"`
- Cost: ~7.5 credits (~$0.75) per 5s clip at time of writing

Iterating on tone is cheap -- e.g. swapping "laughing" for "smiling but not laughing" to dial down the expression took one regeneration. That specific recipe was run through Higgsfield's MCP tool interface (not this app); the "Optional: connect your own Higgsfield account" section above is what lets this app itself do a similar animate step via the public Higgsfield Cloud API instead.

## Notes

- This app is deliberately simple (source + target + run + optional animate). FaceFusion supports a lot more (video, multiple processors, face enhancement, etc.) via its own CLI -- see `facefusion/facefusion.py --help` inside the cloned folder if you want to go further.
- No cloud credits are spent running the face-swap step -- it's all local compute. The optional animate step uses your own Higgsfield credits, at whatever rate your account is billed.
