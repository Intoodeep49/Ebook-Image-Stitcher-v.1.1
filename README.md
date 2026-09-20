# Ebook Image Stitcher 📚📸

An automated, text-aware structural image stitcher built to help students compile long, scrollable textbook sections from digital learning platforms into pristine, continuous PDFs.

This script uses Computer Vision template matching to analyze vertical screenshot streams, automatically locate repeating content seams, purge overlapping lines, and slice away static browser header rows, left/right application menus, user profile names, and floating bottom navigation sliders.

---

## ⚠️ Important Testing Notice
* **Platform Compatibility:** This automation tool was developed and tested exclusively using the **Macmillan Achieve (BFW Publishers)** web book viewer platform interface layout. 
* **Results May Vary:** If you attempt to utilize this script on other e-book publishers or learning systems (like VitalSource, Kindle reader, or alternative web portals), your results may vary. You may need to tweak the constant pixel `TRIM` values at the top of `stitch.py` to match that platform's specific sidebar and header dimensions.

---

## 📋 The Macmillan Achieve Screenshot Method

Because the Macmillan Achieve web reader uses "lazy rendering" (it completely blanks out text lines that aren't actively visible on your monitor screen), standard full-page screenshot extensions will fail. 

To take your snapshots correctly for this script:
1. Open your textbook inside Google Chrome, right-click anywhere on the text column, and choose **Inspect** (or press `F12`).
2. Click the **Device Toolbar icon** at the top-left of the developer panel (it looks like a small phone next to a tablet) to turn on responsive simulation view.
3. Look at the top dimension boxes of your book page frame. Leave the width normal (around `1000`), but change the height box to a massive vertical size like **`8000`** or **`10000`** and hit Enter. This tricks the browser into thinking you have a giant monitor, forcing it to load the hidden paragraphs and images all at once.
4. Scroll all the way down the newly stretched textbook column once to allow the page images to load fully.
5. Click the three vertical dots `⋮` at the very top-right of that *device toolbar line* (not the main browser menu) and select **Capture full size screenshot**.
6. Repeat this down the chapter section, making sure your consecutive captures share at least a few lines of repeating text so the code can lock onto the seams.

---

## ✨ Features
* **Dynamic Batch Processing:** Process multiple chapter sections simultaneously by keeping your images organized inside sequential sub-folders.
* **1-Click Shortcut Execution:** Run the entire script framework straight from your Windows Desktop using a custom application shortcut without opening the Command Prompt window.
* **Complete User Privacy:** Automatically truncates fixed interface rows containing account usernames and metadata before compiling.
* **Automated Organization:** Directs all finalized scrolling documents seamlessly into a dedicated `Completed_Notes` workspace folder and automatically opens it on your screen upon completion.

---

## 🛠️ Required Setup

To run this tool on your machine, you need to install Python along with two core image processing libraries:

```bash
pip install opencv-python Pillow numpy
```

---

## 🚀 How To Use It

### 1. Structure Your Directory
Keep your root workspace organized by creating a sub-folder for each chapter section you wish to compile next to your scripts:

```text
StatsChapters/
├── stitch.py
├── Run_Stitcher.bat
├── Section_1A/           <-- Place your sequential snapshots here (1.png, 2.png, 3.png)
└── Section_1B/           <-- Place your next set of sequential snapshots here
```

### 2. Run the Automation
* Double-click your desktop shortcut driver framework (`Run_Stitcher.bat`).
* The console engine will automatically scan your sub-directories, detect the matching image matrices, purge text duplicates, and export a unified, fluid layout PDF into your newly generated `Completed_Notes` folder, opening it instantly.
