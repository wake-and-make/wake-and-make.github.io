#!/usr/bin/env python3
"""
Convert MOV and MP4 files to WebP format at 30fps with 600px on shorter axis, limited to 8 seconds.
Optimized for smaller file sizes with better compression settings.
"""

import os
import subprocess
import glob

def convert_video_to_webp(input_file, output_file):
    """Convert a video file to WebP with optimized settings for smaller file sizes."""
    # Calculate resolution (600px on shorter axis)
    # First get the original dimensions
    probe_cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json', 
        '-show_streams', input_file
    ]
    
    try:
        result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
        import json
        data = json.loads(result.stdout)
        
        # Find video stream
        video_stream = None
        for stream in data['streams']:
            if stream['codec_type'] == 'video':
                video_stream = stream
                break
        
        if not video_stream:
            print(f"No video stream found in {input_file}")
            return False
        
        # Get original dimensions
        width = int(video_stream['width'])
        height = int(video_stream['height'])
        
        # Check for rotation metadata
        rotation = 0
        if 'side_data_list' in video_stream:
            for side_data in video_stream['side_data_list']:
                if side_data.get('side_data_type') == 'Display Matrix':
                    rotation = side_data.get('rotation', 0)
                    break
        
        # Determine if we need to swap dimensions due to rotation
        needs_rotation = abs(rotation) == 90 or abs(rotation) == 270
        
        if needs_rotation:
            # Swap width and height for rotated videos
            actual_width = height
            actual_height = width
            print(f"Detected {rotation}° rotation, swapping dimensions from {width}x{height} to {actual_width}x{actual_height}")
        else:
            actual_width = width
            actual_height = height
        
        # Calculate new dimensions (600px on shorter axis)
        if actual_width <= actual_height:
            # Portrait or square - width is shorter
            new_width = 600
            new_height = int((actual_height / actual_width) * 600)
        else:
            # Landscape - height is shorter
            new_height = 600
            new_width = int((actual_width / actual_height) * 600)
        
        print(f"Converting {input_file} from {actual_width}x{actual_height} to {new_width}x{new_height}")
        
        # Build video filter - handle rotation properly
        if needs_rotation:
            # Remove rotation metadata - the video content is already correctly oriented
            vf = f'metadata=mode=delete:key=rotate,scale={new_width}:{new_height},fps=30'
        else:
            vf = f'scale={new_width}:{new_height},fps=30'
        
        # Convert to WebP with optimized settings for smaller file sizes
        convert_cmd = [
            'ffmpeg', '-i', input_file,
            '-t', '8',  # Limit to 8 seconds
            '-vf', vf,
            '-c:v', 'libwebp',
            '-quality', '50',        # Even lower quality for smaller files
            '-compression_level', '6', # Higher compression level
            '-preset', 'picture',    # Optimize for pictures/animations
            '-lossless', '0',        # Ensure lossy compression
            '-loop', '0',
            '-y',  # Overwrite output file
            output_file
        ]
        
        subprocess.run(convert_cmd, check=True)
        
        # Get file size for comparison
        input_size = os.path.getsize(input_file) / (1024 * 1024)  # MB
        output_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        compression_ratio = (1 - output_size / input_size) * 100
        
        print(f"Successfully converted {input_file} to {output_file}")
        print(f"  Input: {input_size:.1f}MB → Output: {output_size:.1f}MB ({compression_ratio:.1f}% reduction)")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error converting {input_file}: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error with {input_file}: {e}")
        return False

def main():
    """Convert all video files in the current directory to WebP."""
    # Find all video files
    video_files = glob.glob("*.mov") + glob.glob("*.MOV") + glob.glob("*.mp4") + glob.glob("*.MP4")
    
    if not video_files:
        print("No video files found in current directory")
        return
    
    print(f"Found {len(video_files)} video files to convert:")
    for video_file in video_files:
        print(f"  - {video_file}")
    
    # Convert each file
    converted_count = 0
    skipped_count = 0
    
    for video_file in video_files:
        # Create output filename
        base_name = os.path.splitext(video_file)[0]
        output_file = f"{base_name}.webp"
        
        # Force re-conversion by removing existing files
        if os.path.exists(output_file):
            os.remove(output_file)
            print(f"Removed existing {output_file} for re-conversion")
        
        print(f"\nConverting {video_file}...")
        success = convert_video_to_webp(video_file, output_file)
        
        if success:
            print(f"✓ {video_file} → {output_file}")
            converted_count += 1
        else:
            print(f"✗ Failed to convert {video_file}")
    
    print(f"\nConversion complete: {converted_count} converted, {len(video_files)} total")

if __name__ == "__main__":
    main() 