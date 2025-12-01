def generate_figure_captions(image_paths):
    # Placeholder: usaremos LLaVA cuando integremos GPU (maybe)
    captions = []
    for path in image_paths:
        captions.append({
            "image_path": path,
            "description": f"[Figura extraída: {path.name}]"
        })
    return captions
