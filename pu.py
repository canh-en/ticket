import subprocess

# =========================
# CONFIG
# =========================

# Docker Hub username
DOCKER_USERNAME = "danpc85"

# Version tag
VERSION = "v1"

# List local images
LOCAL_IMAGES = ["nezha"]

# =========================
# DOCKER LOGIN
# =========================
print("===================================")
print("Docker Multi Image Push Script")
print("===================================")

print(f"\n===> Docker login as: {DOCKER_USERNAME}")

subprocess.run(
    ["docker", "login", "-u", DOCKER_USERNAME],
    check=True
)

# =========================
# LOOP PUSH
# =========================
for local_image in LOCAL_IMAGES:

    # ts-ui-dashboard:latest -> ts-ui-dashboard
    image_name = local_image.split(":")[0]

    # remote image
    remote_image = f"{DOCKER_USERNAME}/{image_name}:{VERSION}"

    print("\n-----------------------------------")
    print(f"Local image : {local_image}")
    print(f"Remote image: {remote_image}")

    # =========================
    # TAG
    # =========================
    print("===> Tagging")

    subprocess.run(
        ["docker", "tag", local_image, remote_image],
        check=True
    )

    # =========================
    # PUSH
    # =========================
    print("===> Pushing")

    subprocess.run(
        ["docker", "push", remote_image],
        check=True
    )

# =========================
# DONE
# =========================
print("\n===================================")
print("✅ All images pushed successfully!")
print("===================================")