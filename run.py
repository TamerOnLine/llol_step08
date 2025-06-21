import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from main.config.config_loader import load_env_config
from main.config.db_initializer import ensure_database_exists
from main import create_app
from main.extensions import db

# ✅ تحميل الإعدادات والتحقق من قاعدة البيانات
config = load_env_config()
ensure_database_exists()

# ✅ تهيئة التطبيق
app = create_app()

with app.app_context():
    db.create_all()
    print("✔️ Tables created (if not exist).")

if __name__ == "__main__":
    debug_mode = config.get("FLASK_DEBUG", "True") == "True"
    port = int(config.get("PORT", 40514))
    print(f"🚀 App running on http://0.0.0.0:{port} (debug={debug_mode})")
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
