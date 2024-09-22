import OpenEXR
import Imath
import numpy as np
import PyOpenColorIO as OCIO
import imageio
import os

def convert_exr_to_srgb_png(exr_path, png_output_path, ocio_config_path):
    # Set OCIO environment variable (optional but useful)
    os.environ['OCIO'] = ocio_config_path

    # Load the OCIO config file
    config = OCIO.Config.CreateFromFile(ocio_config_path)
    OCIO.SetCurrentConfig(config)

    # Load the EXR image
    exr_file = OpenEXR.InputFile(exr_path)
    header = exr_file.header()
    dw = header['dataWindow']
    size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)

    # Define the EXR channel format (assuming it's half-float RGB or RGBA)
    FLOAT = Imath.PixelType(Imath.PixelType.FLOAT)
    channels = exr_file.header()['channels'].keys()

    # Check for RGB and Alpha channels
    has_alpha = 'A' in channels

    # Extract RGB channels
    rgb_channels = ['R', 'G', 'B']
    exr_data = [np.frombuffer(exr_file.channel(c, FLOAT), dtype=np.float32).reshape(size[1], size[0]) for c in rgb_channels]

    # Stack RGB channels into a single image array (H, W, C)
    exr_image = np.stack(exr_data, axis=-1)

    # Debugging: Print input EXR image shape and dtype
    print(f"EXR Image Loaded: Shape = {exr_image.shape}, Dtype = {exr_image.dtype}")

    # If alpha exists, handle it separately (we're not passing it through the OCIO transform)
    if has_alpha:
        alpha_channel = np.frombuffer(exr_file.channel('A', FLOAT), dtype=np.float32).reshape(size[1], size[0])
        print("Alpha channel detected and separated.")

    # Create a color transformation from ACEScg to sRGB (or Rec.709, based on what worked)
    try:
        processor = config.getProcessor(OCIO.ColorSpaceTransform(
            src='ACEScg',    # Replace with the correct color space from your config
            dst='Utility - Linear - sRGB'       # Replace with the correct output color space, or try Rec.709 if needed
        ))

        # Check if the processor is valid
        if processor is None:
            raise ValueError("Failed to create OCIO processor.")
        else:
            print("Processor successfully created.")

        # Create a CPU processor for color transformation
        cpu_processor = processor.getDefaultCPUProcessor()

        # Flatten image for RGB transformation
        exr_image_flat = exr_image.reshape((-1, 3))  # Flatten the image into (pixels, 3)
        print(f"Flattened EXR Image: Shape = {exr_image_flat.shape}")

        # Apply the color space conversion
        srgb_image_flat = cpu_processor.applyRGB(exr_image_flat)

        # Check if the transformation returned a valid result
        if srgb_image_flat is None:
            raise ValueError("Color transformation failed. 'applyRGB' returned None.")

        # Reshape back to original image dimensions
        srgb_image = srgb_image_flat.reshape(size[1], size[0], 3)
        print(f"sRGB Image: Shape = {srgb_image.shape}")

        # Clamp values between 0 and 1, then convert to 8-bit for PNG
        srgb_image = np.clip(srgb_image, 0, 1)  # Ensure values are between 0 and 1
        srgb_image = (srgb_image * 255).astype(np.uint8)  # Convert to 8-bit

        # If the EXR had an alpha channel, reattach it to the output PNG
        if has_alpha:
            alpha_channel_clamped = np.clip(alpha_channel, 0, 1)  # Ensure alpha is within [0, 1]
            alpha_channel_uint8 = (alpha_channel_clamped * 255).astype(np.uint8)  # Convert alpha to 8-bit
            srgb_image = np.dstack((srgb_image, alpha_channel_uint8))  # Add alpha channel to sRGB image
            print("Alpha channel reattached to sRGB image.")

        # Save the image as PNG
        imageio.imwrite(png_output_path, srgb_image)
        print(f"Image successfully saved to {png_output_path}")

    except OCIO.Exception as e:
        print(f"OpenColorIO error: {e}")
    except Exception as e:
        print(f"General error: {e}")


# Usage example
ocio_config_path = "W:/guest/3d/ressource/OpenColorIO-Configs-feature-aces-1.2-config/OpenColorIO-Configs-feature-aces-1.2-config/aces_1.2/config.ocio"

# Usage example
convert_exr_to_srgb_png("W:/SBOX/dev2/assets/characters/etst/rendering/_EXPORTS/main_render_LD/0003/RenderPass_Layer_Beauty_1.00111.exr",
                        'output_image.png',
                        ocio_config_path)
