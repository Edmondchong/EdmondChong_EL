import os

def load_products():

    base_folder = "image"
    products = {}

    for category in sorted(os.listdir(base_folder)):

        category_path = os.path.join(base_folder, category)

        if os.path.isdir(category_path):

            products[category] = []

            for file in sorted(os.listdir(category_path)):

                if file.lower().endswith((".jpg", ".png", ".jpeg")):

                    name = os.path.splitext(file)[0].replace("_", " ")

                    image_path = os.path.join(category_path, file)

                    products[category].append({
                        "name": name,
                        "image": image_path
                    })

    return products