import os
import re

# Chạy file này ở thư mục cha chứa:
#   release-0.2.0/

BASE_DIR = os.getcwd()
REPO = os.path.join(BASE_DIR, "release-0.2.0")

# map image cũ -> image mới
REPLACE_MAP = {
    "java:8-jre": "eclipse-temurin:8-jre",
    "java:8": "eclipse-temurin:8-jre",
}

UPDATED = []
SKIPPED = []
NO_DOCKERFILE = []


def patch_dockerfile(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    changed = False

    for old_img, new_img in REPLACE_MAP.items():
        # thay FROM xxx
        pattern = rf'(^\s*FROM\s+){re.escape(old_img)}(\s*$)'
        new_content = re.sub(
            pattern,
            rf'\1{new_img}\2',
            content,
            flags=re.MULTILINE | re.IGNORECASE
        )

        if new_content != content:
            content = new_content
            changed = True

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    return changed


def main():
    if not os.path.isdir(REPO):
        print("❌ Không tìm thấy folder release-0.2.0")
        return

    for name in os.listdir(REPO):
        service_dir = os.path.join(REPO, name)

        if not os.path.isdir(service_dir):
            continue

        dockerfile = os.path.join(service_dir, "Dockerfile")

        if not os.path.isfile(dockerfile):
            NO_DOCKERFILE.append(name)
            continue

        try:
            if patch_dockerfile(dockerfile):
                UPDATED.append(name)
            else:
                SKIPPED.append(name)
        except Exception as e:
            SKIPPED.append(f"{name} (error: {e})")

    print("=" * 60)
    print("DONE PATCH DOCKERFILES")
    print("=" * 60)

    print(f"\nUpdated ({len(UPDATED)}):")
    for x in UPDATED:
        print("  ✔", x)

    print(f"\nNo change ({len(SKIPPED)}):")
    for x in SKIPPED:
        print("  -", x)

    print(f"\nNo Dockerfile ({len(NO_DOCKERFILE)}):")
    for x in NO_DOCKERFILE:
        print("  -", x)


if __name__ == "__main__":
    main()