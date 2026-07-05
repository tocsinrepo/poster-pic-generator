# Poster Pic Generator

A small Streamlit app that puts a **real** face from a photo onto a target image (a poster, thumbnail, generated scene -- whatever) using [FaceFusion](https://github.com/facefusion/facefusion).

This is a **real, deterministic face swap** -- it detects the actual face in your source photo and places it onto the target, instead of asking an AI image model to "redraw" a face from a text description (which is how you end up with extra fingers, swapped positions, or a black eye that was actually a peace-sign hand gesture).

## Why this exists

Built after a July 2026 poster job where an AI image generator kept mangling a real photo reference (Higgsfield / Nano Banana) -- swapping which twin was on which side, and misreading a hand gesture near an eye as an injury. FaceFusion actually detects and swaps the real face pixels, so it doesn't hallucinate.

## Requirements

- A Mac (or any computer) with normal internet access. **This will not work in a network-locked-down sandbox** -- FaceFusion needs to download its face-detection/face-swap models from GitHub and Hugging Face on first run.
- Python 3.10 or newer.
- `git` installed (comes with Xcode Command Line Tools on a Mac).

## Setup (step by step)

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

6. **The first time you click "Run Face Swap"**, two things happen automatically and will take a few minutes:
   - FaceFusion itself gets cloned into a `facefusion/` folder next to the app.
   - FaceFusion downloads its face-detection and face-swap model files the first time it needs them.

   After that first run, everything is cached locally and future swaps are much faster.

7. If FaceFusion's own dependencies aren't installed yet (you'll see an error mentioning a missing package like `onnxruntime` or `opencv`), run:
   ```
   pip install -r facefusion/requirements.txt
   ```
   and try again.

## How to use it

1. Upload your **source photo** -- the real photo containing the face(s) you want to use.
2. Upload your **target image** -- the poster/scene you want that face placed into.
3. If there are two or more people in the source photo, pick the left-to-right (or other) order so FaceFusion matches faces onto the target in the right order.
4. Click **Run Face Swap**.
5. Download the result.

## Turning the finished still into a short video (proven recipe, 2026-07-05)

Once you have a still image you're happy with (face-swapped or not), animating it worked well using **Higgsfield's `kling3_0_turbo` model** with the finished image as the `start_image` reference, rather than any local tool:

- Model: `kling3_0_turbo`
- Input: the approved still image as `start_image`
- Duration: 5s, 720p was plenty for a personal clip
- Prompt style that worked: describe the action/emotion plainly, e.g. `"The two girls celebrate their birthday together — smiling but not laughing, waving, confetti and fireworks bursting behind them, playful joyful energy, subtle natural movement"`
- Cost: ~7.5 credits (~$0.75) per 5s clip at time of writing

Iterating on tone is cheap -- e.g. swapping "laughing" for "smiling but not laughing" to dial down the expression took one regeneration. This step isn't part of this repo's code (it's a direct Higgsfield MCP call, not something FaceFusion does), but documenting it here since it's the natural next step after a face swap and was confirmed working end-to-end on the twins' birthday poster.

## Notes

- This app is deliberately simple (source + target + run). FaceFusion supports a lot more (video, multiple processors, face enhancement, etc.) via its own CLI -- see `facefusion/facefusion.py --help` inside the cloned folder if you want to go further.
- No cloud credits are spent running the face-swap app itself -- it's all local compute on your machine. The video-animation step above does use Higgsfield credits.
