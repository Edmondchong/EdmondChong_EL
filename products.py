import os

def load_products():

    base_folder = "image"
    products = {}

    # ✅ (folder_name, display_name)
    category_order = [
        ("Power System", "⚡ Power System"),
        ("Video System", "🎥 Video System"),
        ("Audio System", "🔊 Audio System"),
        ("Lighting System", "💡 Lighting System"),
    ]

    for folder_name, display_name in category_order:

        category_path = os.path.join(base_folder, folder_name)

        if os.path.isdir(category_path):

            products[display_name] = []

            for file in sorted(os.listdir(category_path)):

                if file.lower().endswith((".jpg", ".png", ".jpeg")):

                    name = os.path.splitext(file)[0].replace("_", " ")

                    image_path = os.path.join(category_path, file)

                    products[display_name].append({
                        "name": name,
                        "image": image_path
                    })

    return products