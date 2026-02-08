import streamlit as st
import pandas as pd
import plotly.express as px

# إعداد الصفحة
st.set_page_config(page_title="Environmental Testing Dashboard", layout="wide")

# 1. تحميل البيانات
@st.cache_data
def load_data():
    try:
        # التعديل هنا: قراءة ملف الإكسل الجديد بدلاً من CSV
        # تأكد أن اسم الملف هنا يطابق تماماً الملف الذي رفعته
        df = pd.read_excel("Smart_Lab_System_Full_Data.xlsx", engine='openpyxl') 
        return df
    except Exception as e:
        # هذا السطر سيظهر لك تفاصيل الخطأ الحقيقي بدلاً من الرسالة العامة
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- الشريط الجانبي (Sidebar) للفلاتر ---
    st.sidebar.header("أدوات الفلترة (Filters)")

    # فلتر العميل
    all_clients = ["All"] + list(df['Client'].unique())
    selected_client = st.sidebar.selectbox("اختر العميل (Client):", all_clients)

    # فلتر نوع العينة (يظهر بناءً على العميل المختار)
    if selected_client != "All":
        filtered_df = df[df['Client'] == selected_client]
    else:
        filtered_df = df

    all_categories = ["All"] + list(filtered_df['Sample Category'].unique())
    selected_category = st.sidebar.selectbox("نوع العينة (Category):", all_categories)

    # تطبيق الفلاتر
    if selected_category != "All":
        filtered_df = filtered_df[filtered_df['Sample Category'] == selected_category]
        
    # فلتر النتيجة (Pass/Fail)
    all_results = ["All"] + list(filtered_df['Conclusion'].unique())
    selected_result = st.sidebar.selectbox("النتيجة (Conclusion):", all_results)
    
    if selected_result != "All":
        filtered_df = filtered_df[filtered_df['Conclusion'] == selected_result]

    # --- واجهة التطبيق الرئيسية ---
    st.title("📊 لوحة تحكم تحاليل البيئة والأغذية")
    st.markdown(f"**عرض البيانات لـ:** {selected_client}")

    # مؤشرات الأداء الرئيسية (KPIs)
    col1, col2, col3 = st.columns(3)
    
    total_samples = len(filtered_df)
    passed_samples = len(filtered_df[filtered_df['Conclusion'] == 'Pass'])
    failed_samples = len(filtered_df[filtered_df['Conclusion'] != 'Pass']) # Assuming anything not Pass is risky
    
    col1.metric("إجمالي الاختبارات", total_samples)
    col2.metric("عدد العينات الناجحة (Pass)", passed_samples, delta_color="normal")
    col3.metric("عدد العينات المخالفة (Fail/Marginal)", failed_samples, delta_color="inverse")

    st.markdown("---")

    # الرسوم البيانية (Charts)
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("توزيع النتائج (Pass vs Fail)")
        if not filtered_df.empty:
            fig_pie = px.pie(filtered_df, names='Conclusion', title='نسبة المطابقة للمواصفات', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        st.subheader("أكثر الاختبارات تكراراً")
        if not filtered_df.empty:
            # نعد أكثر البارامترات تكراراً
            param_counts = filtered_df['Parameter'].value_counts().head(10).reset_index()
            param_counts.columns = ['Parameter', 'Count']
            fig_bar = px.bar(param_counts, x='Count', y='Parameter', orientation='h', title='توزيع الاختبارات')
            st.plotly_chart(fig_bar, use_container_width=True)

    # جدول البيانات التفصيلي
    st.markdown("---")
    st.subheader("📋 تفاصيل البيانات (Data View)")
    st.dataframe(filtered_df, use_container_width=True)

    # زر التحميل
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "تحميل البيانات المفلترة (Excel/CSV)",
        data=csv,
        file_name="Filtered_Report.csv",
        mime="text/csv",
    )

else:

    st.warning("لا توجد بيانات لعرضها. تأكد من تشغيل كود دمج الملفات أولاً.")
