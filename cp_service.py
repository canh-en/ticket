import os
import shutil

# =========================
# CONFIG
# =========================
SRC_ROOT = "release-0.2.0"
DST_ROOT = "mini-ticket"

# 🔥 Chọn service cần copy
SERVICES = [
    "ts-auth-service",
    "ts-user-service",
    "ts-ui-dashboard",
    "ts-verification-code-service",
    "ts-admin-user-service",
    "ts-assurance-service",
    "opentelemetry-javaagent"

    # thêm/bớt tùy bạn
]

# =========================
# MAIN
# =========================
def main():
    print("=== Copy Mini Train Ticket ===")

    # tạo folder đích
    os.makedirs(DST_ROOT, exist_ok=True)

    for service in SERVICES:
        src_path = os.path.join(SRC_ROOT, service)
        dst_path = os.path.join(DST_ROOT, service)

        if not os.path.exists(src_path):
            print(f"❌ Not found: {service}")
            continue

        # nếu đã tồn tại thì xóa trước
        if os.path.exists(dst_path):
            shutil.rmtree(dst_path)

        shutil.copytree(src_path, dst_path)
        print(f"✔ Copied: {service}")

    print("\n🎉 Done!")


if __name__ == "__main__":
    main()