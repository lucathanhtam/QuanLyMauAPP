import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
# Bạn có thể dùng thư viện streamlit-google-auth đã cài ở trên để xử lý login

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Hệ thống Quản lý Mẫu R&D", layout="wide")

# --- KẾT NỐI GOOGLE SHEETS ---
def get_data_from_sheet(sheet_name):
    # Cấu hình đọc file JSON Service Account đã tải ở Bước 3
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('path/to/your/service_account.json', scope)
    client = gspread.authorize(creds)
    
    # Mở file Sheets bằng tên
    sheet = client.open('He_Thong_R&D_Mau').worksheet(sheet_name)
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def append_data_to_sheet(sheet_name, row_data):
    # Hàm này dùng để ghi dữ liệu mới vào tab TONG_HOP_MAU
    pass 

# --- XỬ LÝ ĐĂNG NHẬP GMAIL ---
# (Sử dụng Streamlit-Google-Auth hoặc code logic OAuth2 tại đây)
user_email = "nhanvien@gmail.com" # Giả lập user đã đăng nhập
user_role = "staff" # Giả lập quyền

# --- GIAO DIỆN CHÍNH ---
if not user_email:
    st.write("Vui lòng đăng nhập bằng tài khoản Google (Gmail).")
    # Hiển thị nút Login with Google
else:
    st.sidebar.title(f"Xin chào, {user_email}")
    
    # Phân quyền hiển thị Menu
    if user_role == "admin":
        menu = ["Trang Nhập Liệu", "Dashboard & Dữ Liệu", "Quản lý User"]
    else:
        menu = ["Trang Nhập Liệu"]
        
    choice = st.sidebar.radio("Chọn chức năng:", menu)

    # 1. TRANG NHẬP LIỆU (Mọi người đều thấy)
    if choice == "Trang Nhập Liệu":
        st.header("FORM NHẬP LIỆU MẪU MỚI")
        with st.form("form_nhap_lieu"):
            col1, col2, col3 = st.columns(3)
            with col1:
                khach_hang = st.text_input("Khách hàng (Customer)")
                salesman = st.text_input("Salesman")
            with col2:
                ma_vai = st.text_input("Mã vải (Item Number)")
                thanh_phan = st.text_input("Thành phần (Composition)")
            with col3:
                trang_thai = st.selectbox("Trạng thái", ["Completed", "Weaving", "Dyeing", "Pending"])
            
            # Nút Lưu Data
            submitted = st.form_submit_button("Lưu Dữ Liệu")
            if submitted:
                # Gọi hàm append_data_to_sheet() để đẩy data lên Google Sheets
                st.success("Đã lưu dữ liệu thành công!")
                
    # 2. TRANG DASHBOARD (Chỉ Admin)
    elif choice == "Dashboard & Dữ Liệu":
        st.header("DASHBOARD BÁO CÁO")
        df_tonghop = get_data_from_sheet("TONG_HOP_MAU")
        
        # Tạo biểu đồ đơn giản
        st.subheader("Thống kê Trạng thái")
        trang_thai_count = df_tonghop['Trạng thái (Status)'].value_counts()
        st.bar_chart(trang_thai_count)
        
        # Bảng dữ liệu và Tìm kiếm
        st.subheader("Dữ liệu Tổng hợp")
        search_term = st.text_input("Tìm kiếm theo Mã Vải hoặc Khách hàng...")
        
        if search_term:
            # Lọc dataframe
            df_hien_thi = df_tonghop[df_tonghop.astype(str).apply(lambda x: search_term.lower() in x.to_string().lower(), axis=1)]
        else:
            df_hien_thi = df_tonghop
            
        st.dataframe(df_hien_thi)
        
        # Nút In PDF / Gửi Email (Có thể dùng st.download_button để cho phép tải file)