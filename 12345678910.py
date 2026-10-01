import streamlit as st

# ضبط عنوان الصفحة والتصميم
st.set_page_config(page_title="اضطراب طيف التوحد", page_icon="🧩")

# عنوان التطبيق الرئيسي
st.title("🧩 تطبيق اضطراب طيف التوحد")

st.write("أهلاً بك! تم نشر التطبيق بنجاح عبر منصة Streamlit Cloud.")

# إضافة خانة لإدخال اسم المستخدم أو التفاعل
name = st.text_input("أدخل اسمك هنا:")

if name:
    st.success(f"مرحباً بك {name} في التطبيق!")

# إضافة زر بسيط
if st.button("اضغط هنا"):
    st.balloons()
    st.info("تم الضغط على الزر بنجاح!")
    
