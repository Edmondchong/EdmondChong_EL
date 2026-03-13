import streamlit as st
from products import products
from PIL import Image
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

st.set_page_config(page_title="(XLFM) 技术组 Equipment List", layout="wide")

# cart memory
if "cart" not in st.session_state:
    st.session_state.cart = {}

# order history memory
if "order_history" not in st.session_state:
    st.session_state.order_history = []

st.title("(XLFM) 技术组 Equipment List")

# Clear All Button
if st.button("🧹 Clear All"):

    st.session_state.cart = {}

    for category, product_list in products.items():
        for product in product_list:
            key = f"qty_{category}_{product['name']}"
            st.session_state[key] = 0

    st.rerun()

# Region + Date input
colA, colB = st.columns(2)

with colA:
    region = st.text_input("Region")

with colB:
    date = st.date_input("Date")

# =========================
# Category + Products
# =========================

for category, product_list in products.items():

    with st.expander(category):

        # Clear Category Button
        if st.button(f"🧹 Clear {category}", key=f"clear_{category}"):

            for product in product_list:

                key = f"qty_{category}_{product['name']}"
                st.session_state[key] = 0

                if product["name"] in st.session_state.cart:
                    del st.session_state.cart[product["name"]]

            st.rerun()

        cols = st.columns([1,1,1])

        for i, product in enumerate(product_list):

            with cols[i % 3]:

                st.markdown(f"### {product['name']}")

                img = Image.open(product["image"])
                img = img.resize((230,230))

                st.image(img, use_container_width=True)

                key = f"qty_{category}_{product['name']}"

                if key not in st.session_state:
                    st.session_state[key] = 0

                c1, c2, c3 = st.columns([1,2,1])

                with c1:
                    if st.button("-", key=f"minus_{category}_{product['name']}"):

                        if st.session_state[key] > 0:

                            st.session_state[key] -= 1

                            if st.session_state[key] > 0:
                                st.session_state.cart[product["name"]] = st.session_state[key]
                            elif product["name"] in st.session_state.cart:
                                del st.session_state.cart[product["name"]]

                            st.rerun()

                with c2:
                    st.markdown(
                        f"<h3 style='text-align:center'>{st.session_state[key]}</h3>",
                        unsafe_allow_html=True
                    )

                with c3:
                    if st.button("+", key=f"plus_{category}_{product['name']}"):

                        if st.session_state[key] < 50:

                            st.session_state[key] += 1
                            st.session_state.cart[product["name"]] = st.session_state[key]

                            st.rerun()
# =========================
# Sidebar Cart
# =========================

with st.sidebar:

    st.header("🛒 Cart")

    if len(st.session_state.cart) == 0:
        st.write("Cart is empty")

    else:

        for item, units in st.session_state.cart.items():

            display_name = item.replace("_", " ")
            st.write(f"{display_name}  x  {units}")

        st.divider()

        if st.button("Check Out!"):

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

            # 保存最近订单
            st.session_state.order_history.insert(0, order_data)
            st.session_state.order_history = st.session_state.order_history[:3]

            st.write("### Order Summary")
            st.table(df)

            # =========================
            # Excel
            # =========================

            excel_buffer = BytesIO()

            with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Order")

            excel_data = excel_buffer.getvalue()

            st.download_button(
                label="📥 Download Excel",
                data=excel_data,
                file_name=f"{file_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # =========================
            # PDF
            # =========================

            pdf_buffer = BytesIO()

            data = [["Items", "Quantity"]]

            for item, qty in zip(order_data["Items"], order_data["Quantity"]):
                data.append([item, qty])

            pdf = SimpleDocTemplate(
                pdf_buffer,
                pagesize=A4,
                topMargin=25,
                leftMargin=40,
                rightMargin=40,
            )

            table = Table(data, colWidths=[350,150], hAlign="CENTER")

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

            styles = getSampleStyleSheet()

            title = Paragraph(
                "<b>XLFM Technical Team - Equipment List</b>",
                styles["Title"]
            )

            info = Paragraph(
                f"<font size=11><b>Region :</b> {region}<br/><b>Date :</b> {date_str}</font>",
                styles["Normal"]
            )

            space = Spacer(1,6)

            elements = [title, space, info, space, table]

            pdf.build(elements)

            pdf_buffer.seek(0)

            st.download_button(
                label="📥 Download PDF",
                data=pdf_buffer,
                file_name=f"{file_name}.pdf",
                mime="application/pdf"
            )

    # =========================
    # Recent Orders (Card UI)
    # =========================

    st.divider()
    st.subheader("Recent Orders")

    if len(st.session_state.order_history) == 0:
        st.write("No previous orders")

    else:

        for i, order in enumerate(st.session_state.order_history):

            with st.container(border=True):

                labels = ["🟢 Latest", "🟡 Second Latest", "⚪ Oldest"]
                label = labels[i] if i < len(labels) else f"Order {i+1}"
                
                st.markdown(f"**{label}**")
                st.write(f"Region : {order['Region']}")
                st.write(f"Date : {order['Date']}")

                st.write("Items:")

                for item, qty in zip(order["Items"], order["Quantity"]):
                    st.write(f"{item}  x  {qty}")

                if st.button("Load Order", key=f"load_order_{i}"):

                    # 清空当前 cart
                    st.session_state.cart = {}

                    # reset 所有数量
                    for category, product_list in products.items():
                        for product in product_list:
                            key = f"qty_{category}_{product['name']}"
                            st.session_state[key] = 0

                    # 恢复订单
                    for item, qty in zip(order["Items"], order["Quantity"]):

                        product_name = item.replace(" ", "_")

                        for category, product_list in products.items():
                            for product in product_list:

                                if product["name"] == product_name:

                                    key = f"qty_{category}_{product_name}"

                                    st.session_state[key] = qty
                                    st.session_state.cart[product_name] = qty

                    st.rerun()