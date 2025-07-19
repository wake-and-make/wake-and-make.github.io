#!/usr/bin/env python3
"""
Convert images to red-only versions by mapping luminance to red channel.
Handles both static images and animated WebP files.
"""

from PIL import Image
import os

def convert_to_red(input_path, output_path):
    """Convert an image to red-only by mapping luminance to red channel."""
    # Open the image
    with Image.open(input_path) as img:
        # Check if it's an animated image
        if hasattr(img, 'n_frames') and img.n_frames > 1:
            print(f"Processing animated image with {img.n_frames} frames...")
            convert_animated_to_red(img, output_path)
        else:
            convert_static_to_red(img, output_path)
        
        print(f"Converted {input_path} -> {output_path}")

def convert_static_to_red(img, output_path):
    """Convert a static image to red-only."""
    # Convert to RGB if not already
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Convert to grayscale to get luminance
    gray = img.convert('L')
    
    # Create a new RGB image with red channel from luminance
    red_img = Image.new('RGB', img.size)
    
    # Get the grayscale data
    gray_data = gray.getdata()
    
    # Create red channel data (luminance values)
    red_data = [(pixel, 0, 0) for pixel in gray_data]
    
    # Put the data into the new image
    red_img.putdata(red_data)
    
    # Save the result
    red_img.save(output_path)

def convert_animated_to_red(img, output_path):
    """Convert an animated image to red-only, preserving animation."""
    frames = []
    durations = []
    
    # Process each frame
    for frame_idx in range(img.n_frames):
        img.seek(frame_idx)
        
        # Get frame duration
        try:
            duration = img.info.get('duration', 100)  # Default 100ms
        except:
            duration = 100
        durations.append(duration)
        
        # Convert frame to RGB if needed
        frame = img.convert('RGB')
        
        # Convert to grayscale to get luminance
        gray = frame.convert('L')
        
        # Create a new RGB image with red channel from luminance
        red_frame = Image.new('RGB', frame.size)
        
        # Get the grayscale data
        gray_data = gray.getdata()
        
        # Create red channel data (luminance values)
        red_data = [(pixel, 0, 0) for pixel in gray_data]
        
        # Put the data into the new frame
        red_frame.putdata(red_data)
        
        frames.append(red_frame)
    
    # Save as animated WebP
    if len(frames) > 1:
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0,
            format='WEBP'
        )
    else:
        frames[0].save(output_path, format='WEBP')

def main():
    """Convert all target images to red versions."""
    # List of images to convert
    images = [
        ('demo.webp', 'demo_red.webp'),
        ('2x2x2_v2.jpg', '2x2x2_v2_red.jpg'),
        ('3x3x3_v2.jpg', '3x3x3_v2_red.jpg')
    ]
    
    for input_file, output_file in images:
        if os.path.exists(input_file):
            convert_to_red(input_file, output_file)
        else:
            print(f"Warning: {input_file} not found")

if __name__ == "__main__":
    main() 