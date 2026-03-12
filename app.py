import streamlit as st
from products import products
from PIL import Image
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import streamlit.components.v1 as components

is_mobile = False

@st.cache_data
def load_image(path):
    return Image.open(path)


st.set_page_config(page_title="(XLFM) Technical Team Equipment List System", layout="wide")


# -----------------------------
# UI Scaling
# -----------------------------
if is_mobile:
    IMG_SIZE = 70
    TITLE_SIZE = 14
    QTY_SIZE = 16
    BTN_HEIGHT = 32
    PADDING = 3
else:
    IMG_SIZE = 100
    TITLE_SIZE = 18
    QTY_SIZE = 20
    BTN_HEIGHT = 38
    PADDING = 6
    
# -----------------------------
# UI Font Size
# -----------------------------
st.markdown("""
<style>

/* Label text size */
.stTextInput label,
.stDateInput label {
    font-size:18px !important;
    font-weight:500;
}

/* Label paragraph */
.stTextInput label p,
.stDateInput label p {
    font-size:18px !important;
}

/* Input box text */
.stTextInput input {
    font-size:18px !important;
}

/* =============================
   Mobile Sticky Cart Bar
   ============================= */

.mobile-cart-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #1f1f1f;
    border-top: 2px solid #444;
    padding: 12px 20px;
    z-index: 9999;
}

.mobile-cart-inner {
    max-width: 700px;
    margin: auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.mobile-cart-text {
    font-size: 18px;
    font-weight: 600;
}

.mobile-cart-btn {
    background-color: #ff8c00;
    padding: 8px 16px;
    border-radius: 6px;
    color: white;
    text-decoration: none;
    font-weight: 600;
}

/* =============================
   Reduce Card Spacing
   ============================= */

div[data-testid="stVerticalBlock"] > div {
    padding-top:4px;
    padding-bottom:4px;
}

/* =============================
   Mobile UI Compression
   ============================= */

@media (max-width:768px){

button[kind="secondary"]{
    padding:4px !important;
}

}

/* Reduce main page padding */
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* Reduce card spacing */
div[data-testid="stHorizontalBlock"]{
    gap:8px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# Session Memory
# -----------------------------

if "cart" not in st.session_state:
    st.session_state.cart = {}

if "order_history" not in st.session_state:
    st.session_state.order_history = []


st.title("(XLFM) Technical Team Equipment List System")

if "search_text" not in st.session_state:
    st.session_state.search_text = ""

# -----------------------------
# Region + Date
# -----------------------------

colA, colB = st.columns(2)

with colA:
    region = st.text_input("Region")

with colB:
    date = st.date_input("Date")

col1, col2, col3 = st.columns([5,1,1])

with col1:
    search_input = st.text_input(
        "🔎 Search Equipment",
        value=st.session_state.search_text
    )

with col2:
    st.markdown("<div style='margin-top:32px'></div>", unsafe_allow_html=True)
    if st.button("🔎 Search", use_container_width=True):
        st.session_state.search_text = search_input
        st.rerun()

with col3:
    st.markdown("<div style='margin-top:32px'></div>", unsafe_allow_html=True)
    if st.button("Clear", use_container_width=True):
        st.session_state.search_text = ""
        st.rerun()

search = st.session_state.search_text.lower().strip()

# -----------------------------
# Clear All
# -----------------------------

if st.button("🧹 Clear All Items in Cart"):

    st.session_state.cart = {}

    for category, product_list in products.items():
        for product in product_list:
            key = f"qty_{category}_{product['name']}"
            st.session_state[key] = 0

    st.rerun()

# =========================
# Products
# =========================

for category, product_list in products.items():

    filtered_products = []

    for product in product_list:
        product_name = product["name"].lower().replace("_"," ")

        if search:
            if search.lower() in product_name:
                filtered_products.append(product)
        else:
            filtered_products.append(product)

    if len(filtered_products) == 0:
        continue

    with st.expander(category, expanded=bool(search)):

        if st.button(f"🧹 Clear {category}", key=f"clear_{category}"):

            for product in product_list:

                key = f"qty_{category}_{product['name']}"
                st.session_state[key] = 0

                if product["name"] in st.session_state.cart:
                    del st.session_state.cart[product["name"]]

            st.rerun()

        # -------------------------
        # Product Items
        # -------------------------

        for product in filtered_products:

            with st.container(border=True):

                img = load_image(product["image"])

# -------------------------
# Product Layout
# -------------------------

col_img, col_name = st.columns([1,4])

# Image
with col_img:
    st.image(img, width=IMG_SIZE)

# Item name
with col_name:
    st.markdown(
        f"""
        <div style="
            font-size:{TITLE_SIZE}px;
            font-weight:600;
            margin-top:10px;
        ">
        {product['name']}
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------
# Quantity Buttons (Below)
# -------------------------

key = f"qty_{category}_{product['name']}"

if key not in st.session_state:
    st.session_state[key] = 0

b1, b2, b3 = st.columns([1,1,1])

# Minus button
with b1:

    if st.button(
        "-",
        key=f"minus_{category}_{product['name']}"
    ):

        if st.session_state[key] > 0:

            st.session_state[key] -= 1

            if st.session_state[key] > 0:
                st.session_state.cart[product["name"]] = st.session_state[key]
            elif product["name"] in st.session_state.cart:
                del st.session_state.cart[product["name"]]

            st.rerun()

# Quantity
with b2:

    st.markdown(
        f"<p style='text-align:center;font-size:{QTY_SIZE}px'>{st.session_state[key]}</p>",
        unsafe_allow_html=True
    )

# Plus button
with b3:

    if st.button(
        "+",
        key=f"plus_{category}_{product['name']}"
    ):

        if st.session_state[key] < 50:

            st.session_state[key] += 1
            st.session_state.cart[product["name"]] = st.session_state[key]

            st.rerun()

# =========================
# Mobile Sticky Cart Bar
# =========================

if is_mobile:

    total_items = sum(st.session_state.cart.values())

    if total_items > 0:

        st.markdown(
            f"""
            <div class="mobile-cart-bar">
                <div class="mobile-cart-inner">

                    <div class="mobile-cart-text">
                        🛒 {total_items} items in cart
                    </div>

                    <a href="#sidebar" class="mobile-cart-btn">
                        Open Cart
                    </a>

                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
# =========================
# Sidebar Cart
# =========================

with st.sidebar:
    
    st.markdown("<a name='sidebar'></a>", unsafe_allow_html=True)

    if len(st.session_state.cart) == 0:

        st.header("🛒 Cart")
        st.write("Cart is empty")

    else:

        total_items = sum(st.session_state.cart.values())

        st.header(f"🛒 Cart ({total_items} items)")

        for category, product_list in products.items():

            category_items = []
            category_total = 0

            for product in product_list:

                name = product["name"]

                if name in st.session_state.cart:

                    qty = st.session_state.cart[name]

                    category_items.append((name.replace("_"," "), qty))
                    category_total += qty

            if category_items:

                with st.expander(f"{category} ({category_total})", expanded=True):

                    for item, qty in category_items:

                        product_anchor = item.replace(" ", "_")

                        st.markdown(f"""
                        <a href="#{product_anchor}" style="text-decoration:none;">
                            <div style="
                                padding:10px;
                                margin-bottom:8px;
                                border-radius:10px;
                                background-color:#1f1f1f;
                                border:1px solid #333;
                                display:flex;
                                justify-content:space-between;
                                align-items:center;
                            ">
                                <div style="font-weight:600;">{item}</div>
                                <div style="
                                    font-size:15px;
                                    color:#ffb84d;
                                    font-weight:600;
                                ">
                                    x{qty}
                                </div>
                            </div>
                        </a>
                        """, unsafe_allow_html=True)

        st.divider()

        # =========================
        # Checkout
        # =========================

        if st.button("🚀 Check Out!", use_container_width=True):

            if region.strip() == "":
                st.warning("Please enter Region before Checkout!")
                st.stop()

            safe_region = region.replace(" ", "_")
            date_str = date.strftime("%d-%m-%Y")
            file_name = f"{safe_region}_{date_str}"

            st.success("Order Confirmed!")

            order_data = {
                "Region": region,
                "Date": date_str,
                "Items": [item.replace("_", " ") for item in st.session_state.cart.keys()],
                "Quantity": list(st.session_state.cart.values())
            }

            df = pd.DataFrame({
                "Items": order_data["Items"],
                "Quantity": order_data["Quantity"]
            })

            # Save order history
            st.session_state.order_history.insert(0, order_data)
            st.session_state.order_history = st.session_state.order_history[:3]

            st.write("### Order Summary")
            st.table(df)

            # =========================
            # Excel
            # =========================

            excel_buffer = BytesIO()

            excel_rows = []

            for category, product_list in products.items():

                for product in product_list:

                    name = product["name"]

                    if name in st.session_state.cart:

                        excel_rows.append([
                            category,
                            name.replace("_"," "),
                            st.session_state.cart[name]
                        ])

            df_excel = pd.DataFrame(excel_rows, columns=["Category", "Item", "Quantity"])

            with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:

                df_excel.to_excel(writer, index=False, startrow=3, sheet_name="Order")

                workbook  = writer.book
                worksheet = writer.sheets["Order"]

                # Write Region and Date
                worksheet.write("A1", f"Region : {region}")
                worksheet.write("A2", f"Date : {date_str}")

                # Adjust column width
                worksheet.set_column("A:A", 20)
                worksheet.set_column("B:B", 35)
                worksheet.set_column("C:C", 10)

                header_format = workbook.add_format({
                    "bold": True,
                    "border": 1
                })

                for col_num, value in enumerate(df_excel.columns.values):
                    worksheet.write(3, col_num, value, header_format)

            st.download_button(
                "📥 Download Excel",
                data=excel_buffer.getvalue(),
                file_name=f"{file_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # =========================
            # PDF
            # =========================

            pdf_buffer = BytesIO()

            pdf = SimpleDocTemplate(
                pdf_buffer,
                pagesize=A4,
                topMargin=25,
                leftMargin=40,
                rightMargin=40,
            )

            elements = []

            styles = getSampleStyleSheet()

            title = Paragraph(
                "<b>XLFM Technical Team - Equipment List</b>",
                styles["Title"]
            )

            info = Paragraph(
                f"<font size=11><b>Region :</b> {region}<br/><b>Date :</b> {date_str}</font>",
                styles["Normal"]
            )

            elements.append(title)
            elements.append(Spacer(1,10))
            elements.append(info)
            elements.append(Spacer(1,10))

            for category, product_list in products.items():

                category_items = []

                for product in product_list:

                    name = product["name"]

                    if name in st.session_state.cart:
                        qty = st.session_state.cart[name]
                        category_items.append((name.replace("_"," "), qty))

                if category_items:

                    data = [[f"{category} (Items)", "Quantity"]]

                    for item, qty in category_items:
                        data.append([item, qty])

                    table = Table(data, colWidths=[380,120], hAlign="CENTER")

                    table.setStyle(TableStyle([
                        ("BACKGROUND", (0,0), (-1,0), colors.orange),
                        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                        ("GRID", (0,0), (-1,-1), 1, colors.black),
                        ("ALIGN", (1,1), (1,-1), "CENTER"),
                        ("ALIGN", (0,0), (-1,0), "CENTER"),
                        ("FONTSIZE", (0,0), (-1,-1), 11),
                        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
                        ("TOPPADDING", (0,0), (-1,-1), 4),
                    ]))

                    elements.append(table)
                    elements.append(Spacer(1,12))

            pdf.build(elements)

            pdf_buffer.seek(0)

            st.download_button(
                "📥 Download PDF",
                data=pdf_buffer,
                file_name=f"{file_name}.pdf",
                mime="application/pdf"
            )


    # =========================
    # Recent Orders
    # =========================

    st.divider()

    st.markdown(
        "<p style='font-size:12px; color:gray'>"
        "Developed by Edmond<br>"
        "System support contact: Edmond"
        "</p>",
        unsafe_allow_html=True
    )

    st.subheader("Recent Orders")

    if len(st.session_state.order_history) == 0:

        st.write("No previous orders")

    else:

        for i, order in enumerate(st.session_state.order_history):

            with st.container():

                labels = ["🟢 Latest", "🟡 Second Latest", "⚪ Oldest"]
                label = labels[i] if i < len(labels) else f"Order {i+1}"

                st.markdown(f"**{label}**")
                st.write(f"Region : {order['Region']}")
                st.write(f"Date : {order['Date']}")

                st.write("Items:")

                for item, qty in zip(order["Items"], order["Quantity"]):
                    st.write(f"{item}  x  {qty}")

                if st.button("Load Order", key=f"load_order_{i}"):

                    st.session_state.cart = {}

                    for category, product_list in products.items():
                        for product in product_list:
                            key = f"qty_{category}_{product['name']}"
                            st.session_state[key] = 0

                    for item, qty in zip(order["Items"], order["Quantity"]):

                        product_name = item.replace(" ", "_")

                        for category, product_list in products.items():
                            for product in product_list:

                                if product["name"] == product_name:

                                    key = f"qty_{category}_{product_name}"

                                    st.session_state[key] = qty
                                    st.session_state.cart[product_name] = qty

                    st.rerun()