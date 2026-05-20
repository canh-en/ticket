import os

# =========================
# CONFIG
# =========================
PREFIX = "danpc85"
VERSION = "0.2.0"

# root repo
BASE_PATH = os.getcwd()

# =========================
# OPTIONS
# =========================

# push image lên Docker Hub hay không
PUSH = True

# xóa image local sau khi push
# giúp tiết kiệm dung lượng Codespace
REMOVE_AFTER_PUSH = True

# build lại Maven jar hay không
#
# True:
#   mvn clean package
#
# False:
#   dùng lại jar cũ trong target/
#
BUILD_MAVEN = False

# =========================
# MANUAL SERVICES
# =========================
# [] -> auto scan mọi folder có Dockerfile
#
# Ví dụ:
# SERVICES = ["ts-auth-service"]
#
SERVICES = []

SUCCESS = []
FAILED = []


# =========================
# AUTO DISCOVER SERVICES
# =========================
def discover_services():
    services = []

    for item in os.listdir(BASE_PATH):
        path = os.path.join(BASE_PATH, item)

        # chỉ lấy thư mục
        if not os.path.isdir(path):
            continue

        # bỏ qua hidden folder
        if item.startswith("."):
            continue

        dockerfile = os.path.join(path, "Dockerfile")

        # có Dockerfile -> là service
        if os.path.exists(dockerfile):
            services.append(item)

    return sorted(services)


# =========================
# MAIN
# =========================
def main():
    print("=== Build Mini Ticket ===")

    print(f"PUSH = {PUSH}")
    print(f"REMOVE_AFTER_PUSH = {REMOVE_AFTER_PUSH}")
    print(f"BUILD_MAVEN = {BUILD_MAVEN}")

    # xác định service cần build
    services = SERVICES or discover_services()

    print("\n📦 Services:")
    for s in services:
        print(" -", s)

    if not services:
        print("❌ No service found")
        return

    # =========================
    # Maven build
    # =========================
    if BUILD_MAVEN:
        if not mvn_build():
            print("❌ Maven build failed")
            return
    else:
        print("\n⏭️ Skip Maven build")

    # =========================
    # Docker login
    # =========================
    if PUSH:
        docker_login()

    # =========================
    # Build từng service
    # =========================
    for service in services:
        build_service(service)

    summary()


# =========================
# Maven build
# =========================
def mvn_build():
    print("\n🔨 Maven build in container...")

    cmd = (
        "docker run --rm "
        f"-v {BASE_PATH}:/app "
        "-w /app "
        "maven:3.8.6-openjdk-8 "
        "mvn clean package -Dmaven.test.skip=true"
    )

    return os.system(cmd) == 0


# =========================
# Docker login
# =========================
def docker_login():
    print(f"\n🔐 Docker login: {PREFIX}")

    if os.system(f"docker login --username={PREFIX}") != 0:
        exit("❌ Docker login failed")


# =========================
# Cleanup docker image
# =========================
def cleanup_image(tag):
    print(f"\n🧹 Removing image: {tag}")

    # remove image
    os.system(f"docker rmi -f {tag}")

    # cleanup dangling images
    os.system("docker image prune -f")

    # cleanup build cache
    os.system("docker builder prune -f")

    print("✅ Cleanup done")


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

    # =========================
    # PUSH
    # =========================
    if PUSH:
        print(f"📤 Pushing {tag}")

        if os.system(f"docker push {tag}") != 0:
            print(f"❌ Push failed: {service}")
            FAILED.append(service)
            return

        print(f"✅ Pushed: {tag}")

        # =========================
        # REMOVE IMAGE
        # =========================
        if REMOVE_AFTER_PUSH:
            cleanup_image(tag)

    SUCCESS.append(service)


# =========================
# SUMMARY
# =========================
def summary():
    print("\n=========================")
    print("===== BUILD SUMMARY =====")
    print("=========================")

    print(f"\n✅ Success ({len(SUCCESS)}):")
    for s in SUCCESS:
        print("  ✔", s)

    print(f"\n❌ Failed ({len(FAILED)}):")
    for s in FAILED:
        print("  ✘", s)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    main()