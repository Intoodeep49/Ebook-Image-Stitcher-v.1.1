import os
import re
import cv2
import numpy as np
from PIL import Image

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

# --- INTERFACE TRIMMING CONSTANTS ---
GLOBAL_TOP_HEADER_TRIM = 350     
GLOBAL_LEFT_SIDEBAR_TRIM = 310   
GLOBAL_RIGHT_SIDEBAR_TRIM = 210  
LAST_PAGE_FOOTER_TRIM = 300      

def clean_page_frame(img_path, is_last_page=False):
    img = cv2.imread(img_path)
    if img is None:
        return None
    h, w, _ = img.shape
    bottom_boundary = h - LAST_PAGE_FOOTER_TRIM if is_last_page else h
    cropped = img[GLOBAL_TOP_HEADER_TRIM : bottom_boundary, GLOBAL_LEFT_SIDEBAR_TRIM : w - GLOBAL_RIGHT_SIDEBAR_TRIM]
    return cropped

def process_folder(folder_path, folder_name, output_dir):
    image_extensions = ('.png', '.PNG')
    all_files = os.listdir(folder_path)
    image_files = sorted([os.path.join(folder_path, f) for f in all_files if f.endswith(image_extensions) and "Perfect" not in f], key=natural_sort_key)
    
    if len(image_files) < 2:
        print(f" -> Skipping [{folder_name}]: Needs at least 2 raw screenshots.")
        return

    print(f"\nProcessing [{folder_name}] with {len(image_files)} images...")
    current_canvas = clean_page_frame(image_files[0], is_last_page=False)

    for idx in range(1, len(image_files)):
        is_last = (idx == len(image_files) - 1)
        next_img = clean_page_frame(image_files[idx], is_last_page=is_last)
        if next_img is None:
            continue
            
        template_height = 90
        template = next_img[0:template_height, :]
        search_start_y = int(current_canvas.shape[0] * 0.4)
        search_region = current_canvas[search_start_y:, :]
        
        match_result = cv2.matchTemplate(search_region, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(match_result)
        
        if max_val > 0.65:
            match_y = max_loc[1] + search_start_y
            canvas_top = current_canvas[0:match_y, :]
            current_canvas = np.vstack((canvas_top, next_img))
        else:
            current_canvas = np.vstack((current_canvas, next_img))

    final_rgb = cv2.cvtColor(current_canvas, cv2.COLOR_BGR2RGB)
    pil_pdf = Image.fromarray(final_rgb)
    
    output_name = f"{folder_name}_Continuous_Textbook.pdf"
    full_output_path = os.path.join(output_dir, output_name)
    
    pil_pdf.save(full_output_path, "PDF", resolution=100.0)
    print(f"🎉 Success! Moved output to: '{full_output_path}'")

# --- MAIN BATCH CONTROLLER ---
if __name__ == "__main__":
    current_directory = "."
    items = os.listdir(current_directory)
    
    output_folder = "Completed_Notes"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created dedicated output folder: '{output_folder}'")
    
    subfolders = [d for d in items if os.path.isdir(os.path.join(current_directory, d)) and not d.startswith('.') and d != output_folder]
    
    if not subfolders:
        print("No batch sub-folders found. Sticking to current main folder layout...")
        process_folder(current_directory, "Main_Chapter", output_folder)
    else:
        print(f"Found {len(subfolders)} sub-folders to process automatically.")
        for folder in sorted(subfolders):
            full_path = os.path.join(current_directory, folder)
            process_folder(full_path, folder, output_folder)
        print("\nAll batch processing completed successfully!")

    # NEW: Automatically open the Completed_Notes window right on your desktop screen!
    try:
        os.startfile(output_folder)
    except Exception:
        pass

input("\nPress ENTER to exit...")
