from flask import render_template, request, redirect, url_for, flash
from app import app
from .forms import URLForm
import os
import sys

# Tính toán đường dẫn chính xác
current_file = os.path.abspath(__file__)  # Web/app/routes.py
app_dir = os.path.dirname(current_file)   # Web/app/
web_dir = os.path.dirname(app_dir)        # Web/
project_root = os.path.dirname(web_dir)   # Review_Seeding_Detection_System/

# Thêm project root vào Python path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print(f"Project root: {project_root}")
print(f"Shopee path exists: {os.path.exists(os.path.join(project_root, 'Shopee'))}")

try:
    from Shopee.browser_automation import run_browser_automation
    print("✅ Successfully imported browser_automation")
except ImportError as e:
    print(f"❌ Import error: {e}")
    # Thử import trực tiếp
    try:
        import importlib.util
        browser_automation_path = os.path.join(project_root, 'Shopee', 'browser_automation.py')
        print(f"Trying direct import from: {browser_automation_path}")
        
        spec = importlib.util.spec_from_file_location("browser_automation", browser_automation_path)
        browser_automation_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(browser_automation_module)
        
        run_browser_automation = browser_automation_module.run_browser_automation
        print("✅ Direct import successful")
    except Exception as direct_error:
        print(f"❌ Direct import failed: {direct_error}")
        run_browser_automation = None

@app.route('/', methods=['GET', 'POST'])
def index():
    form = URLForm()
    if form.validate_on_submit():
        url = form.url.data
        
        # Kiểm tra và thêm http:// nếu chưa có
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        print(f"🔗 Đang gửi URL đến browser automation: {url}")
        
        if run_browser_automation is None:
            flash('❌ Không thể kết nối đến browser automation module!', 'error')
            return redirect(url_for('index'))
        
        try:
            # Gọi browser automation
            result = run_browser_automation(url)
            
            if result.get("success"):
                flash(f'✅ Đã mở thành công trang: {result.get("title", "Unknown")}', 'success')
            else:
                flash(f'❌ Lỗi khi mở URL: {result.get("error", "Unknown error")}', 'error')
                
        except Exception as e:
            flash(f'💥 Có lỗi xảy ra: {str(e)}', 'error')
            print(f"Exception in browser automation: {e}")
        
        return redirect(url_for('index'))
        
    return render_template('index.html', form=form)