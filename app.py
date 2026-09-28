import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials # DÙNG THƯ VIỆN MỚI

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Hệ thống Quản lý Mẫu R&D", layout="wide")

# --- KẾT NỐI GOOGLE SHEETS ---
SHEET_NAME = 'He_Thong_R&D_Mau' 

def get_google_client():
    """Khởi tạo kết nối với Google Sheets sử dụng Streamlit Secrets."""
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    # Đọc thông tin xác thực từ Streamlit Secrets
    # Dùng st.secrets["gcp_service_account"] tương ứng với biến bạn đặt ở Bước 1
    credentials_dict = {
        "type": st.secrets["gcp_service_account"]["type"],
        "project_id": st.secrets["gcp_service_account"]["project_id"],
        "private_key_id": st.secrets["gcp_service_account"]["private_key_id"],
        "private_key": st.secrets["gcp_service_account"]["private_key"],
        "client_email": st.secrets["gcp_service_account"]["client_email"],
        "client_id": st.secrets["gcp_service_account"]["client_id"],
        "auth_uri": st.secrets["gcp_service_account"]["auth_uri"],
        "token_uri": st.secrets["gcp_service_account"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["gcp_service_account"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["gcp_service_account"]["client_x509_cert_url"],
    }
    
    creds = Credentials.from_service_account_info(credentials_dict, scopes=scope)
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
        return pd.DataFrame() 

def append_data_to_sheet(tab_name, row_data):
    """Ghi một dòng dữ liệu mới vào tab cụ thể."""
    client = get_google_client()
    sheet = client.open(SHEET_NAME).worksheet(tab_name)
    sheet.append_row(row_data)

# --- QUẢN LÝ TRẠNG THÁI (SESSION STATE) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = ""

# --- GIAO DIỆN ĐĂNG NHẬP ---
def login_view():
    st.title("Đăng nhập Hệ thống R&D")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            email = st.text_input("Email (Sử dụng Gmail)")
            password = st.text_input("Mật khẩu", type="password", help="Tạm thời nhập bất kỳ ký tự nào để test")
            
            submit = st.form_submit_button("Đăng nhập")
            
            if submit:
                if email.endswith("@gmail.com"):
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    
                    if email == "admin@gmail.com": # Đổi thành email quản trị của bạn
                        st.session_state.user_role = "admin"
                    else:
                        st.session_state.user_role = "staff"
                        
                    st.rerun() 
                else:
                    st.error("Vui lòng sử dụng địa chỉ email hợp lệ (@gmail.com).")

# --- GIAO DIỆN CHÍNH ---
def main_app_view():
    st.sidebar.title(f"Xin chào,\n{st.session_state.user_email}")
    if st.sidebar.button("Đăng xuất"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.user_role = ""
        st.rerun()
        
    st.sidebar.markdown("---")
    
    if st.session_state.user_role == "admin":
        menu = ["Trang Nhập Liệu", "Dashboard & Dữ Liệu"]
    else:
        menu = ["Trang Nhập Liệu"]
        
    choice = st.sidebar.radio("Chọn chức năng:", menu)

    # 1. TRANG NHẬP LIỆU
    if choice == "Trang Nhập Liệu":
        st.header("FORM NHẬP LIỆU MẪU MỚI")
        with st.form("form_nhap_lieu", clear_on_submit=True): 
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
                if not khach_hang or not salesman or not ma_vai:
                    st.warning("Vui lòng điền đầy đủ các trường có dấu *.")
                else:
                    try:
                        row_to_insert = [khach_hang, ma_vai, trang_thai, salesman, thanh_phan]
                        
                        # Thay "Trang_tinh_1" bằng tên tab thực tế
                        append_data_to_sheet("Trang_tinh_1", row_to_insert) 
                        
                        st.success("Đã lưu dữ liệu thành công!")
                    except Exception as e:
                        st.error(f"Lỗi khi lưu dữ liệu lên Sheet: {e}")
                        
    # 2. TRANG DASHBOARD
    elif choice == "Dashboard & Dữ Liệu":
        st.header("DASHBOARD BÁO CÁO")
        
        # Thay "Trang_tinh_1" bằng tên tab thực tế
        df_tonghop = get_data_from_sheet("Trang_tinh_1")
        
        if not df_tonghop.empty:
            st.subheader("Thống kê Trạng thái")
            # Nếu cột tên là "Trạng thái (Status)", hãy sửa lại bên dưới cho đúng
            if "Trạng thái" in df_tonghop.columns: 
                trang_thai_count = df_tonghop['Trạng thái'].value_counts()
                st.bar_chart(trang_thai_count)
            else:
                st.info("Không tìm thấy cột 'Trạng thái' để vẽ biểu đồ.")
            
            st.subheader("Dữ liệu Tổng hợp")
            search_term = st.text_input("Tìm kiếm...")
            
            if search_term:
                df_hien_thi = df_tonghop[df_tonghop.astype(str).apply(lambda x: search_term.lower() in x.to_string().lower(), axis=1)]
            else:
                df_hien_thi = df_tonghop
                
            st.dataframe(df_hien_thi)
        else:
            st.warning("Không có dữ liệu hoặc không kết nối được với Sheet.")

# --- LUỒNG ĐIỀU HƯỚNG ---
if not st.session_state.logged_in:
    login_view()
else:
    main_app_view()
