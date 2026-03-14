# unitywebcheck

Tools for inspecting and extracting assets from Unity `.data.unityweb` build files. You can list every asset (textures, audio clips, meshes, etc.) with its size, or count how many audio clips are in a build.

## What's in this repo

| File | What it does |
|------|-------------|
| `getinfo.py` | Lists all assets inside extracted Unity data, sorted by size (largest first). Shows the type, size in MB, and name of each asset. |
| `count_unity_type.py` | Counts the number of entries of a given asset type (e.g. AudioClip, Texture2D) in extracted Unity data. |
| `count_unity_types.py` | Shows counts for every asset type found, sorted most common first, with a total. |
| `report_unity_types.py` | Generates a full report of all asset types — counts, sizes, and type-specific details (dimensions, duration, sample rate, etc.). |
| `run_all.py` | One-command workflow: extracts a `.data.unityweb` file and runs all reports, saving each to a separate text file. |
| `requirements.txt` | Lists the Python packages these scripts need. |

## Prerequisites

You need **Python 3** installed on your computer.

### Check if Python is already installed

**macOS:**

Open **Terminal** (search for "Terminal" in Spotlight, or find it in Applications > Utilities) and type:

```
python3 --version
```

If you see something like `Python 3.12.x`, you're good. If not, install it from [python.org/downloads](https://www.python.org/downloads/).

**Windows:**

Open **Command Prompt** (search for "cmd" in the Start menu) and type:

```
python --version
```

If you see something like `Python 3.12.x`, you're good. If not, install it from [python.org/downloads](https://www.python.org/downloads/). During installation, **check the box that says "Add Python to PATH"** — this is important.

> **Note for Windows users:** On Windows, the Python command is usually `python` (not `python3`). The rest of this guide uses `python3` — if that doesn't work for you, try `python` instead.

---

## Setup (one-time)

These steps create an isolated workspace so the tools' dependencies don't interfere with anything else on your system. You only need to do this once.

### 1. Download or clone this repo

Put the files somewhere convenient, for example on your Desktop. Open a terminal and navigate to the folder:

**macOS:**
```
cd ~/Desktop/unitywebcheck
```

**Windows:**
```
cd %USERPROFILE%\Desktop\unitywebcheck
```

### 2. Create a virtual environment

A "virtual environment" is a private folder where Python installs packages just for this project, keeping your system clean.

**macOS:**
```
python3 -m venv .env
```

**Windows:**
```
python -m venv .env
```

### 3. Activate the virtual environment

You need to activate it each time you open a new terminal window to use these tools.

**macOS:**
```
source .env/bin/activate
```

**Windows (Command Prompt):**
```
.env\Scripts\activate
```

**Windows (PowerShell):**
```
.env\Scripts\Activate.ps1
```

When activated, you'll see `(.env)` at the beginning of your terminal prompt.

### 4. Install required packages

```
pip install -r requirements.txt
```

### 5. Fix the uwdtool import bug

The `uwdtool` package has a bug where it tries to import `brotli` using the wrong path. You need to fix two files.

Find your Python version number (e.g. `3.12`) — it will match whatever `python3 --version` showed you earlier.

**macOS** — open each file in a text editor:

```
open -a TextEdit .env/lib/python3.12/site-packages/uwdtool/BinaryReader.py
open -a TextEdit .env/lib/python3.12/site-packages/uwdtool/CompressionManager.py
```

**Windows** — open each file in Notepad:

```
notepad .env\Lib\site-packages\uwdtool\BinaryReader.py
notepad .env\Lib\site-packages\uwdtool\CompressionManager.py
```

In **both files**, find this line:

```python
import uwdtool.brotli.brotli as brotli
```

and change it to:

```python
import brotli
```

Save both files and close the editor.

---

## Usage

Make sure your virtual environment is activated first (you should see `(.env)` in your prompt — if not, run the activate command from step 3 above).

### Inspect a .data.unityweb file

Use `uwdtool` to see what's inside a Unity web data file:

```
uwdtool --inspect -i path/to/your/file.data.unityweb
```

To save the report to a file instead of printing it on screen:

```
uwdtool --inspect -i path/to/your/file.data.unityweb > report.txt
```

### Extract files from a .data.unityweb file

```
uwdtool --unpack -i path/to/your/file.data.unityweb -o extracted
```

This creates a folder called `extracted` containing the unpacked data.

### List all assets with sizes

After extracting, run `getinfo.py` on the extracted folder:

```
python3 getinfo.py extracted/
```

This prints a table of all assets, sorted largest first:

```
        MB  Type                  Source      Name
------------------------------------------------------------------------------------------
      0.06  AudioClip             m_Resource  112_DANI_2
      0.06  AudioClip             m_Resource  82_DANI_81
      0.06  AnimationClip         object      ToppoLesson_1_Gesture1_TalkingVer
```

### Count entries by asset type

Specify the type you want to count as a second argument:

```
python3 count_unity_type.py extracted/ AudioClip
```

Output:

```
AudioClip: 1163
```

You can count any Unity asset type, for example:

```
python3 count_unity_type.py extracted/ Texture2D
python3 count_unity_type.py extracted/ Mesh
python3 count_unity_type.py extracted/ AnimationClip
```

### Count all asset types

To see counts for every type at once:

```
python3 count_unity_types.py extracted/
```

Example output:

```
Type                               Count    Total Size
------------------------------  --------  ------------
GameObject                          8423      519.7 KB
MonoBehaviour                       8388       4.06 MB
Transform                           4482      349.0 KB
RectTransform                       3941      461.9 KB
MonoScript                          3413      384.2 KB
CanvasRenderer                      2689       34.1 KB
AudioClip                           1163      105.5 KB
MeshFilter                           905       21.2 KB
MeshRenderer                         879      138.9 KB
Texture2D                            600      88.46 MB
Mesh                                 474      14.92 MB
MeshCollider                         366       22.9 KB
BoxCollider                          315       20.9 KB
Sprite                               289      687.0 KB
...
```

### Full report of all asset types

For a comprehensive breakdown of everything in the extracted data:

```
python3 report_unity_types.py extracted/
```

This prints a summary table of all types with counts and sizes, followed by a detail section for each type with type-specific columns (dimensions, duration, sample rate, etc.). Types with no extra metadata show name and size.

Example output (abbreviated):

```
======================================================================
Cubemap  (6 objects)
======================================================================
  Name                                                            Size
  ------------------------------------------------------- ------------
  Cubemap_U4Skybox                                             2.08 MB
  Cubemap_Unit4Sunset                                          1.50 MB
  RefProbe_BaseCamp                                           928.6 KB
  Cookie_AlienCircuits                                        512.2 KB
  Default-Skybox-Cubemap                                      512.2 KB
  Cookie_Noise                                                384.2 KB

======================================================================
AnimationClip  (139 objects)
======================================================================
  Name                                                Size   Length  SampleRate
  --------------------------------------------- ---------- -------- -----------
  Animation Clip_GA_Tera_idle02                   300.0 KB                 60.0
  Animation Clip_Aryn_idle02                      259.6 KB                 60.0
  Anderson_U1_WorkingonMachine                    249.0 KB                 30.0
  Player_LookAround                               203.9 KB                 30.0
  U3_Crate_PickupFail                             194.9 KB                 30.0
  ...
```

You can redirect the output to a file for easier review:

```
python3 report_unity_types.py extracted/ > full_report.txt
```

### Run everything at once

Instead of running each step manually, use `run_all.py` to extract and generate all reports in one command:

```
python3 run_all.py /path/to/unit4.data.unityweb
```

This creates a timestamped folder (e.g. `unit4_20260313_141500/`) containing:

| File | Contents |
|------|----------|
| `extracted/` | The unpacked Unity data |
| `uwdtool_inspect.txt` | Raw uwdtool inspection output |
| `getinfo.txt` | All assets sorted by size |
| `count_unity_types.txt` | Counts and total size per type |
| `count_audioclip.txt` | AudioClip count |
| `report_unity_types.txt` | Full detailed report |

---

## Quick reference

Here's the typical workflow end-to-end:

**macOS:**
```bash
cd ~/Desktop/unitywebcheck
source .env/bin/activate
uwdtool --unpack -i /path/to/unit4.data.unityweb -o extracted
python3 getinfo.py extracted/
python3 count_unity_type.py extracted/ AudioClip
python3 count_unity_types.py extracted/
python3 report_unity_types.py extracted/
```

**Windows:**
```cmd
cd %USERPROFILE%\Desktop\unitywebcheck
.env\Scripts\activate
uwdtool --unpack -i C:\path\to\unit4.data.unityweb -o extracted
python getinfo.py extracted/
python count_unity_type.py extracted/ AudioClip
python count_unity_types.py extracted/
python report_unity_types.py extracted/
```

## Troubleshooting

- **"python3 is not recognized"** (Windows) — Use `python` instead of `python3`.
- **"No module named UnityPy"** — Make sure your virtual environment is activated (you should see `(.env)` in your prompt), then run `pip install -r requirements.txt`.
- **"No module named brotli"** or errors from uwdtool about brotli — Make sure you applied the import fix in step 5.
- **PowerShell says "running scripts is disabled"** — Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` and try again.
