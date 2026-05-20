import os
import shutil

# =========================
# CONFIG
# =========================
PREFIX = "danpc85"
VERSION = "0.2.2"
# PROXY = "172.20.1.22/proxy-cache"   # nếu không dùng thì để ""
PROXY = ""

# Chọn service cần build
# [] = build tất cả ts-*
# ["ts-user-service"] = build 1 service
ONLY_SERVICES = []

BASE_PATH = os.getcwd()
BUILD_PATHS = []


# =========================
# MAIN
# =========================
def main():
    print("=== TrainTicket Build Tool (Container Maven Java8) ===")

    if not mvn_build_in_container():
        print("❌ Maven build failed")
        return

    init_build_paths()

    if not BUILD_PATHS:
        print("❌ No services found")
        return

    docker_login()
    docker_build_push_clean()


# =========================
# STEP 1: Maven Build in Docker
# =========================
def mvn_build_in_container():
    print("🔨 Maven build using container Java8...")

    cmd = (
        "docker run --rm "
        f"-v {BASE_PATH}:/app "
        "-w /app "
        "maven:3.8.6-openjdk-8 "
        "mvn clean package -DskipTests"
    )

    return os.system(cmd) == 0


# =========================
# STEP 2: Find services
# =========================
def init_build_paths():
    for name in os.listdir(BASE_PATH):
        full_path = os.path.join(BASE_PATH, name)

        if os.path.isdir(full_path) and name.startswith("ts-"):

            if ONLY_SERVICES and name not in ONLY_SERVICES:
                continue

            BUILD_PATHS.append(full_path)

    print(f"📦 Found {len(BUILD_PATHS)} service(s)")


# =========================
# STEP 3: Docker Login
# =========================
def docker_login():
    print(f"🔐 Docker Hub Login: {PREFIX}")

    status = os.system(f"docker login --username={PREFIX}")

    if status != 0:
        print("❌ Docker login failed")
        exit(1)

    print("✅ Docker login success")


# =========================
# STEP 4: Docker Build + Push + Clean
# =========================
def docker_build_push_clean():
    for path in BUILD_PATHS:
        os.chdir(path)

        service = os.path.basename(path)
        tag = f"{PREFIX}/{service}:{VERSION}"

        if not os.path.exists("Dockerfile"):
            print(f"⏭️ Skip {service} (no Dockerfile)")
            continue

        print(f"\n🚀 Building {tag}")

        if PROXY:
            build_cmd = (
                f"docker build . "
                f"--build-arg prox={PROXY} "
                f"-t {tag}"
            )
        else:
            build_cmd = f"docker build . -t {tag}"

        if os.system(build_cmd) != 0:
            print(f"❌ Build failed: {service}")
            continue

        print(f"✅ Build success: {service}")

        print(f"📤 Pushing {tag}")

        if os.system(f"docker push {tag}") != 0:
            print(f"❌ Push failed: {service}")
            continue

        print(f"✅ Push success: {service}")

        print(f"🗑 Remove local image {tag}")
        os.system(f"docker rmi {tag}")

        print("🧹 Clean docker cache")
        os.system("docker image prune -f")

        show_disk()

    os.chdir(BASE_PATH)


# =========================
# STEP 5: Disk Usage
# =========================
def show_disk():
    total, used, free = shutil.disk_usage("/")
    gb = 1024 ** 3

    print(f"💽 Free Disk: {free // gb} GB / {total // gb} GB")


# =========================
# RUN
# =========================
if __name__ == "__main__":
    main()