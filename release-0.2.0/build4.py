import os
import shutil
import glob
import requests

# =========================
# CONFIG
# =========================
PREFIX = "danpc85"
VERSION = "0.2.2"
PROXY = ""

ONLY_SERVICES = ["ts-avatar-service"]
FORCE_MAVEN = False

BASE_PATH = os.getcwd()
BUILD_PATHS = []

SUCCESS = []
FAILED = []
SKIPPED = []

# =========================
# CHECK SERVICE TYPE
# =========================
def is_java_service(service):
    return os.path.exists(os.path.join(BASE_PATH, service, "pom.xml"))


# =========================
# CHECK TAG EXISTS
# =========================
def tag_exists(repo, tag):
    url = f"https://hub.docker.com/v2/repositories/{repo}/tags/{tag}"
    try:
        r = requests.get(url, timeout=5)
        return r.status_code == 200
    except:
        return False


# =========================
# MAIN
# =========================
def main():
    print("=== TrainTicket Smart Build Tool ===")

    if need_run_maven():
        print("🔨 Running Maven (Java services)...")
        if not mvn_build_in_container():
            print("❌ Maven build failed")
            return
    else:
        print("✅ Skip Maven (jar exists or non-Java services)")

    init_build_paths()

    if not BUILD_PATHS:
        print("❌ No services found")
        return

    docker_login()
    docker_build_push_clean()
    print_summary()


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
        if not is_java_service(service):
            continue

        target = os.path.join(BASE_PATH, service, "target")
        jars = glob.glob(os.path.join(target, "*.jar"))

        if not jars:
            print(f"📦 No jar found (Java): {service}")
            return True

    return False


# =========================
# Maven Build
# =========================
def mvn_build_in_container():
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

        service = os.path.basename(path)
        repo = f"{PREFIX}/{service}"
        tag = f"{repo}:{VERSION}"

        dockerfile_path = os.path.join(service, "Dockerfile")

        if not os.path.exists(dockerfile_path):
            print(f"⏭️ Skip {service} (no Dockerfile)")
            SKIPPED.append(service)
            continue

        # skip nếu tag đã tồn tại
        if tag_exists(repo, VERSION):
            print(f"⏭️ Skip {service} (tag exists)")
            SKIPPED.append(service)
            continue

        print(f"\n🚀 Building {tag}")

        os.chdir(BASE_PATH)

        build_cmd = (
            f"docker build -f {dockerfile_path} . "
            f"--build-arg prox={PROXY} -t {tag}"
            if PROXY else
            f"docker build -f {dockerfile_path} . -t {tag}"
        )

        if os.system(build_cmd) != 0:
            print(f"❌ Build failed: {service}")
            FAILED.append(service)
            continue

        print("✅ Build success")

        print(f"📤 Pushing {tag}")

        if os.system(f"docker push {tag}") != 0:
            print(f"❌ Push failed: {service}")
            FAILED.append(service)
            continue

        print("✅ Push success")

        SUCCESS.append(service)

        os.system(f"docker rmi {tag}")
        os.system("docker image prune -f")

        show_disk()

    os.chdir(BASE_PATH)


# =========================
# SUMMARY
# =========================
def print_summary():
    print("\n" + "=" * 60)
    print("BUILD SUMMARY")
    print("=" * 60)

    print(f"\n✅ Success ({len(SUCCESS)}):")
    for s in SUCCESS:
        print("  ✔", s)

    print(f"\n❌ Failed ({len(FAILED)}):")
    for s in FAILED:
        print("  -", s)

    print(f"\n⏭️ Skipped ({len(SKIPPED)}):")
    for s in SKIPPED:
        print("  -", s)


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