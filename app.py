from math import erf

import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Hệ thống Quản lý Mẫu R&D", layout="wide")

# --- KẾT NỐI GOOGLE SHEETS ---
# CHÚ Ý QUAN TRỌNG: Bạn cần thay đổi tên file JSON và tên Sheet cho đúng với thực tế của bạn
SERVICE_ACCOUNT_FILE = 'he_thong_mau_key.json' # Đảm bảo file JSON này nằm cùng thư mục với app.py
SHEET_NAME = 'He_Thong_R&D_Mau' 

def get_google_client():
    """Khởi tạo kết nối với Google Sheets."""
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
    return gspread.authorize(creds)

def get_data_from_sheet(tab_name):
    """Đọc dữ liệu từ một tab cụ thể."""
    try:
        client = get_google_client()
        sheet = client.open(SHEET_NAME).worksheet(tab_name)
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Lỗi khi đọc dữ liệu từ tab {tab_name}: {e}")
        return pd.DataFrame() # Trả về DataFrame rỗng nếu lỗi

def append_data_to_sheet(tab_name, row_data):
    """Ghi một dòng dữ liệu mới vào tab cụ thể."""
    client = get_google_client()
    sheet = client.open(SHEET_NAME).worksheet(tab_name)
    sheet.append_row(row_data)

# --- QUẢN LÝ TRẠNG THÁI (SESSION STATE) ---
# Khởi tạo các biến để theo dõi việc người dùng đã đăng nhập hay chưa
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = ""

# --- GIAO DIỆN ĐĂNG NHẬP ---
def login_view():
    st.title("Đăng nhập Hệ thống R&D")
    
    # Tạo một hộp (container) nhỏ ở giữa màn hình cho form đăng nhập
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            email = st.text_input("Email (Sử dụng Gmail)")
            password = st.text_input("Mật khẩu", type="password", help="Tạm thời nhập bất kỳ ký tự nào để test")
            
            submit = st.form_submit_button("Đăng nhập")
            
            if submit:
                # LOGIC KIỂM TRA TẠM THỜI
                if email.endswith("@gmail.com"):
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    
                    # Cấp quyền admin nếu là email cụ thể (bạn thay email của bạn vào đây)
                    if email == "admin@gmail.com": 
                        st.session_state.user_role = "admin"
                    else:
                        st.session_state.user_role = "staff"
                        
                    st.rerun() # Tải lại trang để áp dụng trạng thái mới
                else:
                    st.error("Vui lòng sử dụng địa chỉ email hợp lệ (@gmail.com).")

# --- GIAO DIỆN CHÍNH (SAU KHI ĐĂNG NHẬP) ---
def main_app_view():
    # Sidebar
    st.sidebar.title(f"Xin chào,\n{st.session_state.user_email}")
    if st.sidebar.button("Đăng xuất"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.user_role = ""
        st.rerun()
        
    st.sidebar.markdown("---")
    
    # Phân quyền Menu
    if st.session_state.user_role == "admin":
        menu = ["Trang Nhập Liệu", "Dashboard & Dữ Liệu"]
    else:
        menu = ["Trang Nhập Liệu"]
        
    choice = st.sidebar.radio("Chọn chức năng:", menu)

    # 1. TRANG NHẬP LIỆU (Staff & Admin)
    if choice == "Trang Nhập Liệu":
        st.header("FORM NHẬP LIỆU MẪU MỚI")
        with st.form("form_nhap_lieu", clear_on_submit=True): # clear_on_submit giúp xoá trắng form sau khi lưu thành công
            col1, col2, col3 = st.columns(3)
            with col1:
                khach_hang = st.text_input("Khách hàng (Customer)*")
                salesman = st.text_input("Salesman*")
            with col2:
                ma_vai = st.text_input("Mã vải (Item Number)*")
                thanh_phan = st.text_input("Thành phần (Composition)")
            with col3:
                trang_thai = st.selectbox("Trạng thái", ["Completed", "Weaving", "Dyeing", "Pending"])
            
            submitted = st.form_submit_button("Lưu Dữ Liệu")
            
            if submitted:
                # Kiểm tra các trường bắt buộc
                if not khach_hang or not salesman or not ma_vai:
                    st.warning("Vui lòng điền đầy đủ các trường có dấu *.")
                else:
                    try:
                        # 1. Chuẩn bị danh sách dữ liệu để lưu
                        # LƯU Ý: Thứ tự các biến trong danh sách này PHẢI KHỚP với thứ tự cột trong Google Sheet của bạn
                        # Giả sử sheet của bạn chỉ có 5 cột này để test:
                        row_to_insert = [khach_hang, ma_vai, trang_thai, salesman, thanh_phan]
                        
                        # 2. Gọi hàm lưu (Nhớ thay "Trang_tinh_1" bằng tên Tab thực tế trong file Sheet)
                        append_data_to_sheet("Data_Mau", row_to_insert) 
                        
                        st.success("Đã lưu dữ liệu thành công!")
                    except Exception as e:
                        # Nếu có lỗi (như sai tên sheet, chưa cấp quyền Editor), nó sẽ in ra đây
                        st.error(f"Lỗi khi lưu dữ liệu lên Sheet: {e}")
                        
    # 2. TRANG DASHBOARD (Chỉ Admin)
    elif choice == "Dashboard & Dữ Liệu":
        st.header("DASHBOARD BÁO CÁO")
        
        # Nhớ thay "Trang_tinh_1" bằng tên Tab chứa dữ liệu của bạn
        df_tonghop = get_data_from_sheet("Data_Mau")
        
        if not df_tonghop.empty:
            # Tạo biểu đồ đơn giản
            st.subheader("Thống kê Trạng thái")
            # Giả định tên cột trong sheet là "Trạng thái". Thay đổi nếu tên cột của bạn khác.
            if "Trạng thái" in df_tonghop.columns: 
                trang_thai_count = df_tonghop['Trạng thái'].value_counts()
                st.bar_chart(trang_thai_count)
            else:
                st.info("Không tìm thấy cột 'Trạng thái' để vẽ biểu đồ.")
            
            # Bảng dữ liệu và Tìm kiếm
            st.subheader("Dữ liệu Tổng hợp")
            search_term = st.text_input("Tìm kiếm...")
            
            if search_term:
                df_hien_thi = df_tonghop[df_tonghop.astype(str).apply(lambda x: search_term.lower() in x.to_string().lower(), axis=1)]
            else:
                df_hien_thi = df_tonghop
                
            st.dataframe(df_hien_thi)
        else:
            st.warning("Không có dữ liệu hoặc không kết nối được với Sheet.")

# --- LUỒNG ĐIỀU HƯỚNG CHÍNH ---
if not st.session_state.logged_in:
    # Nếu chưa đăng nhập, chỉ hiện form login
    login_view()
else:
    # Nếu đã đăng nhập, hiện ứng dụng chính
    main_app_view()
