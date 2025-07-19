#!/usr/bin/env python3
"""
Convert images to red-only versions preserving luminance.
Takes source and target directories as command line arguments.
"""

import os
import sys
from PIL import Image, ImageEnhance
import argparse
from tqdm import tqdm

def convert_to_red_only(image_path, output_path):
    """Convert an image to red-only while preserving luminance."""
    try:
        # Open the image
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Get image data
            width, height = img.size
            pixels = img.load()
            
            # Create new image for red-only version
            red_img = Image.new('RGB', (width, height), (0, 0, 0))
            red_pixels = red_img.load()
            
            # Process each pixel
            for x in range(width):
                for y in range(height):
                    r, g, b = pixels[x, y]
                    
                    # Calculate luminance (standard formula)
                    luminance = 0.299 * r + 0.587 * g + 0.114 * b
                    
                    # Convert to red-only while preserving luminance
                    red_value = int(luminance)
                    red_pixels[x, y] = (red_value, 0, 0)
            
            # Save the red-only image
            red_img.save(output_path, 'PNG')
            return True
            
    except Exception as e:
        print(f"Error converting {image_path}: {e}")
        return False

def convert_animated_webp_to_red(image_path, output_path):
    """Convert animated WebP to red-only while preserving animation."""
    try:
        with Image.open(image_path) as img:
            # Check if it's animated
            if hasattr(img, 'n_frames') and img.n_frames > 1:
                # Process all frames
                frames = []
                durations = []
                
                # Progress bar for frames
                with tqdm(total=img.n_frames, desc=f"Converting {os.path.basename(image_path)}", unit="frame") as pbar:
                    for frame_idx in range(img.n_frames):
                        img.seek(frame_idx)
                        
                        # Convert frame to RGB if necessary
                        frame = img.convert('RGB')
                        
                        # Get frame data
                        width, height = frame.size
                        pixels = frame.load()
                        
                        # Create new frame for red-only version
                        red_frame = Image.new('RGB', (width, height), (0, 0, 0))
                        red_pixels = red_frame.load()
                        
                        # Process each pixel
                        for x in range(width):
                            for y in range(height):
                                r, g, b = pixels[x, y]
                                
                                # Calculate luminance
                                luminance = max(r, g, b)
                                
                                # Convert to red-only while preserving luminance
                                red_value = int(luminance)
                                red_pixels[x, y] = (red_value, 0, 0)
                        
                        frames.append(red_frame)
                        
                        # Get frame duration
                        if hasattr(img, 'info') and 'duration' in img.info:
                            durations.append(img.info['duration'])
                        else:
                            durations.append(100)  # Default 100ms
                        
                        pbar.update(1)
                
                # Save as animated WebP
                if frames:
                    frames[0].save(
                        output_path,
                        'WEBP',
                        save_all=True,
                        append_images=frames[1:],
                        duration=durations,
                        loop=0
                    )
                    return True
            else:
                # Not animated, use regular conversion
                return convert_to_red_only(image_path, output_path)
                
    except Exception as e:
        print(f"Error converting animated {image_path}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Convert images to red-only versions')
    parser.add_argument('source_dir', help='Source directory containing images')
    parser.add_argument('target_dir', help='Target directory for red-only images')
    
    args = parser.parse_args()
    
    # Create target directory if it doesn't exist
    os.makedirs(args.target_dir, exist_ok=True)
    
    # Supported image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp'}
    
    # Find all image files in source directory
    image_files = []
    for filename in os.listdir(args.source_dir):
        file_path = os.path.join(args.source_dir, filename)
        
        # Check if it's a file and has image extension
        if os.path.isfile(file_path):
            _, ext = os.path.splitext(filename.lower())
            if ext in image_extensions:
                image_files.append(filename)
    
    if not image_files:
        print("No image files found in source directory")
        return
    
    print(f"Found {len(image_files)} image files to convert")
    
    # Convert files with progress bar
    converted_count = 0
    skipped_count = 0
    with tqdm(total=len(image_files), desc="Converting images", unit="file") as pbar:
        for filename in image_files:
            file_path = os.path.join(args.source_dir, filename)
            output_path = os.path.join(args.target_dir, filename)
            
            # Check if output file already exists
            if os.path.exists(output_path):
                print(f"Skipping {filename} - already exists in target directory")
                skipped_count += 1
                pbar.update(1)
                continue
            
            # Handle different file types
            _, ext = os.path.splitext(filename.lower())
            if ext == '.webp':
                success = convert_animated_webp_to_red(file_path, output_path)
            else:
                success = convert_to_red_only(file_path, output_path)
            
            if success:
                converted_count += 1
            
            pbar.update(1)
    
    print(f"\nConversion complete: {converted_count} converted, {skipped_count} skipped, {len(image_files)} total")

if __name__ == "__main__":
    main() 