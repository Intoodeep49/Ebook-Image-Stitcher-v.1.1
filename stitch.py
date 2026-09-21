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
DEFAULT_FOOTER_TRIM = 300        # Base trim to clear out standard bottom margins
MAX_PDF_HEIGHT_LIMIT = 64000     # Safety window beneath absolute 65,500 pixel ceiling

def clean_page_frame(img_path):
    img = cv2.imread(img_path)
    if img is None:
        return None
    h, w, _ = img.shape
    # Slice off the static sidebar/header boundaries uniformly
    cropped = img[GLOBAL_TOP_HEADER_TRIM : h, GLOBAL_LEFT_SIDEBAR_TRIM : w - GLOBAL_RIGHT_SIDEBAR_TRIM]
    return cropped

def process_folder(folder_path, folder_name, output_dir):
    image_extensions = ('.png', '.PNG')
    all_files = os.listdir(folder_path)
    image_files = sorted([os.path.join(folder_path, f) for f in all_files if f.endswith(image_extensions) and "Perfect" not in f], key=natural_sort_key)
    
    if len(image_files) < 2:
        print(f" -> Skipping [{folder_name}]: Needs at least 2 raw screenshots.")
        return

    print(f"\nProcessing [{folder_name}] with {len(image_files)} images...")
    
    # Correctly targets the FIRST image string frame array to open the canvas
    current_canvas = clean_page_frame(image_files[0])

    for idx in range(1, len(image_files)):
        next_img = clean_page_frame(image_files[idx])
        if next_img is None:
            continue
            
        template_height = 90
        template = next_img[0:template_height, :]
        search_start_y = int(current_canvas.shape[0] * 0.4)
        search_region = current_canvas[search_start_y:, :]
        
        match_result = cv2.matchTemplate(search_region, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(match_result)
        
        if max_val > 0.65:
            match_y = max_loc[0] + search_start_y
            canvas_top = current_canvas[0:match_y, :]
            current_canvas = np.vstack((canvas_top, next_img))
        else:
            current_canvas = np.vstack((current_canvas, next_img))

    # Apply the base 300px cut option to the final canvas bottom boundary first
    c_h, c_w, _ = current_canvas.shape
    current_canvas = current_canvas[0 : c_h - DEFAULT_FOOTER_TRIM, :]

    # Convert the unified canvas array to RGB format
    final_rgb = cv2.cvtColor(current_canvas, cv2.COLOR_BGR2RGB)
    full_height, full_width, _ = final_rgb.shape
    
    output_name = f"{folder_name}_Continuous_Textbook.pdf"
    full_output_path = os.path.join(output_dir, output_name)

    # DYNAMIC HEIGHT PROTECTION CHECK WITH TARGETED LAST PAGE EXTRA CROP
    if full_height > MAX_PDF_HEIGHT_LIMIT:
        print(f" -> Canvas height ({full_height}px) exceeds safe limits. Splitting into multiple PDF pages dynamically...")
        page_list = []
        current_y = 0
        
        while current_y < full_height:
            chunk_h = min(MAX_PDF_HEIGHT_LIMIT, full_height - current_y)
            page_chunk = final_rgb[current_y : current_y + chunk_h, :]
            
            # Applying the extra 150px layout trim to the final page chunk if height limit is crossed
            if current_y + chunk_h >= full_height:
                print(f" -> Applying extra 150px layout trim to the bottom of the final page chunk.")
                p_h, p_w, _ = page_chunk.shape
                page_chunk = page_chunk[0 : p_h - 150, :]
                
            page_list.append(Image.fromarray(page_chunk))
            current_y += chunk_h
            
        # Compile sub-pages sequentially into a unified multi-page PDF document
        page_list[0].save(full_output_path, "PDF", resolution=100.0, save_all=True, append_images=page_list[1:])
    else:
        # Standard single-page compilation handles the base trim perfectly
        pil_pdf = Image.fromarray(final_rgb)
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

    try:
        os.startfile(output_folder)
    except Exception:
        pass

input("\nPress ENTER to exit...")
