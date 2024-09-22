import PyOpenColorIO as OCIO

def test_color_processor(ocio_config_path):
    # Load the OCIO config file
    config = OCIO.Config.CreateFromFile(ocio_config_path)
    OCIO.SetCurrentConfig(config)

    # List available color spaces
    print("Available Color Spaces:")
    for cs in config.getColorSpaces():
        print(cs.getName())

    try:
        # Try to create a processor from ACEScg to sRGB
        processor = config.getProcessor(OCIO.ColorSpaceTransform(
            src='ACEScg',   # Use exact name from the list
            dst='Output - sRGB'      # Use exact name from the list
        ))

        print("Processor successfully created.")
        return processor
    
    except OCIO.Exception as e:
        print(f"OpenColorIO error: {e}")
    except Exception as e:
        print(f"General error: {e}")

# Usage
ocio_config_path = "W:/guest/3d/ressource/OpenColorIO-Configs-feature-aces-1.2-config/OpenColorIO-Configs-feature-aces-1.2-config/aces_1.2/config.ocio"
processor = test_color_processor(ocio_config_path)
