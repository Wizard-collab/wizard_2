import subprocess
import os
import cv2
import PyOpenColorIO as ocio

os.environ['PATH'] += os.pathsep + "binaries/ffmpeg/bin"

def convert_exr_to_mp4(exr_sequence_path, output_mp4_path, fps=24):
    # Define the FFmpeg command to convert EXR sequence to MP4
    ffmpeg_command = [
        'ffmpeg',
        '-start_number', '100',
        '-framerate', str(fps),
        '-i', exr_sequence_path,
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        output_mp4_path
    ]

    # Run the FFmpeg command
    subprocess.run(ffmpeg_command, check=True)

def apply_aces_ocio(input_mp4_path, output_mp4_path):
    # Load the ACES configuration
    config = ocio.Config.CreateFromFile('W:/guest/3d/ressource/OpenColorIO-Configs-feature-aces-1.2-config/OpenColorIO-Configs-feature-aces-1.2-config/aces_1.2/config.ocio')


    # Define the source and destination color spaces
    src_color_space = config.getColorSpace('ACES - ACEScg')
    dst_color_space = config.getColorSpace('Output - sRGB')

    # Create the processor
    processor = config.getProcessor(src_color_space, dst_color_space)

    # Read the input MP4 file
    cap = cv2.VideoCapture(input_mp4_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {input_mp4_path}")
        return

    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_mp4_path, fourcc, fps, (frame_width, frame_height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Apply the color transformation
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = processor.apply(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Write the frame to the output video
        out.write(frame)

    # Release everything if the job is finished
    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    exr_sequence_path = 'W:/SCRIPT/wizard_2/exrs_test/%04d.exr'
    intermediate_mp4_path = 'intermediate.mp4'
    final_mp4_path = 'final_output.mp4'

    # Convert EXR sequence to MP4
    convert_exr_to_mp4(exr_sequence_path, intermediate_mp4_path)

    # Apply ACES OCIO transformation
    apply_aces_ocio(intermediate_mp4_path, final_mp4_path)

    print(f"Conversion complete. Output saved to {final_mp4_path}")
