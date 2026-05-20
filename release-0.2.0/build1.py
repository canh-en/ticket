import os
import shutil
import glob

# =========================
# CONFIG
# =========================
PREFIX = "danpc85"
VERSION = "0.2.2"
PROXY = ""

# [] = build all ts-*
ONLY_SERVICES = []

# True = force run maven
# False = auto detect jar
FORCE_MAVEN = False

BASE_PATH = os.getcwd()
BUILD_PATHS = []


# =========================
# MAIN
# =========================
def main():
    print("=== TrainTicket Smart Build Tool ===")

    if need_run_maven():
        if not mvn_build_in_container():
            print("❌ Maven build failed")
            return
    else:
        print("✅ Skip Maven (jar exists)")

    init_build_paths()

    if not BUILD_PATHS:
        print("❌ No services found")
        return

    docker_login()
    docker_build_push_clean()


# =========================
# Detect Need Maven
# =========================
def need_run_maven():
    if FORCE_MAVEN:
        return True

    services = ONLY_SERVICES if ONLY_SERVICES else [
        x for x in os.listdir(BASE_PATH)
        if x.startswith("ts-")
    ]

    for service in services:
        target = os.path.join(BASE_PATH, service, "target")
        jars = glob.glob(os.path.join(target, "*.jar"))

        if not jars:
            print(f"📦 No jar found: {service}")
            return True

    return False


# =========================
# Maven Build
# =========================
def mvn_build_in_container():
    print("🔨 Maven build in Java8 container...")

    cmd = (
        "docker run --rm "
        f"-v {BASE_PATH}:/app "
        "-w /app "
        "maven:3.8.6-openjdk-8 "
        "mvn clean package -DskipTests"
    )

    return os.system(cmd) == 0


# =========================
# Find Services
# =========================
def init_build_paths():
    for name in os.listdir(BASE_PATH):
        full = os.path.join(BASE_PATH, name)

        if os.path.isdir(full) and name.startswith("ts-"):

            if ONLY_SERVICES and name not in ONLY_SERVICES:
                continue

            BUILD_PATHS.append(full)

    print(f"📦 Found {len(BUILD_PATHS)} service(s)")


# =========================
# Docker Login
# =========================
def docker_login():
    print(f"🔐 Docker login: {PREFIX}")

    if os.system(f"docker login --username={PREFIX}") != 0:
        exit("❌ Login failed")

    print("✅ Login success")


# =========================
# Build Push Clean
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

        build_cmd = (
            f"docker build . --build-arg prox={PROXY} -t {tag}"
            if PROXY else
            f"docker build . -t {tag}"
        )

        if os.system(build_cmd) != 0:
            print(f"❌ Build failed: {service}")
            continue

        print("✅ Build success")

        if os.system(f"docker push {tag}") != 0:
            print(f"❌ Push failed: {service}")
            continue

        print("✅ Push success")

        os.system(f"docker rmi {tag}")
        os.system("docker image prune -f")

        show_disk()

    os.chdir(BASE_PATH)


# =========================
# Disk
# =========================
def show_disk():
    total, used, free = shutil.disk_usage("/")
    gb = 1024 ** 3

    print(f"💽 Free: {free // gb} GB / {total // gb} GB")


# =========================
# RUN
# =========================
if __name__ == "__main__":
    main()