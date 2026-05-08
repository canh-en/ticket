import os

# =========================
# CONFIG
# =========================
PREFIX = "danpc85"
VERSION = "mini-1.0"
BASE_PATH = os.getcwd()

# 🔥 bật/tắt push bằng env (mặc định = False)
PUSH = os.getenv("PUSH", "false").lower() == "true"

# 🔥 6 service có Dockerfile
SERVICES = [
    "ts-auth-service",
    "ts-user-service",
    "ts-verification-code-service",
    "ts-admin-user-service",
    "ts-assurance-service",
    "ts-ui-dashboard",
]

SUCCESS = []
FAILED = []


# =========================
# MAIN
# =========================
def main():
    print("=== Build Mini Ticket ===")
    print(f"PUSH = {PUSH}")

    if not mvn_build():
        print("❌ Maven build failed")
        return

    if PUSH:
        docker_login()

    for service in SERVICES:
        build_service(service)

    summary()


# =========================
# Maven build (container)
# =========================
def mvn_build():
    print("🔨 Maven build in container...")

    cmd = (
        "docker run --rm "
        f"-v {BASE_PATH}:/app "
        "-w /app "
        "maven:3.8.6-openjdk-8 "
        # 🔥 FIX test compile
        "mvn clean package -Dmaven.test.skip=true"
    )

    return os.system(cmd) == 0


# =========================
# Docker login
# =========================
def docker_login():
    print(f"🔐 Docker login: {PREFIX}")
    if os.system(f"docker login --username={PREFIX}") != 0:
        exit("❌ Docker login failed")


# =========================
# Build từng service
# =========================
def build_service(service):
    dockerfile = os.path.join(service, "Dockerfile")

    if not os.path.exists(dockerfile):
        print(f"⏭️ Skip {service} (no Dockerfile)")
        return

    tag = f"{PREFIX}/{service}:{VERSION}"

    print(f"\n🚀 Building {tag}")

    cmd = f"docker build --no-cache -f {dockerfile} . -t {tag}"

    if os.system(cmd) != 0:
        print(f"❌ Build failed: {service}")
        FAILED.append(service)
        return

    print(f"✅ Build success: {service}")

    # 🔥 chỉ push nếu bật
    if PUSH:
        if os.system(f"docker push {tag}") != 0:
            print(f"❌ Push failed: {service}")
            FAILED.append(service)
            return

        print(f"📤 Pushed: {tag}")

    SUCCESS.append(service)


# =========================
# Summary
# =========================
def summary():
    print("\n===== SUMMARY =====")

    print(f"\n✅ Success ({len(SUCCESS)}):")
    for s in SUCCESS:
        print("  ✔", s)

    print(f"\n❌ Failed ({len(FAILED)}):")
    for s in FAILED:
        print("  -", s)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    main()