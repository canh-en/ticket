import os
import shutil

# Đang đứng ở folder cha chứa 2 repo
BASE_DIR = os.getcwd()

SRC_REPO = os.path.join(BASE_DIR, "Augmented-TrainTicket")
DST_REPO = os.path.join(BASE_DIR, "release-0.2.0")

COPIED = []
SKIPPED = []
NOT_FOUND = []

for service_name in os.listdir(SRC_REPO):
    src_service = os.path.join(SRC_REPO, service_name)

    # chỉ xử lý folder service bắt đầu bằng ts-
    if not os.path.isdir(src_service):
        continue
    if not service_name.startswith("ts-"):
        continue

    # file nguồn logback.xml trong Augmented
    src_logback = os.path.join(
        src_service,
        "src",
        "main",
        "resources",
        "logback.xml"
    )

    # nếu repo bạn là logbackxml không có dấu chấm thì thử thêm fallback
    alt_src_logback = os.path.join(
        src_service,
        "src",
        "main",
        "resources",
        "logbackxml"
    )

    if os.path.isfile(src_logback):
        real_src = src_logback
    elif os.path.isfile(alt_src_logback):
        real_src = alt_src_logback
    else:
        NOT_FOUND.append(service_name)
        continue

    # service tương ứng bên release
    dst_service = os.path.join(DST_REPO, service_name)

    if not os.path.isdir(dst_service):
        SKIPPED.append(service_name)
        continue

    dst_resource = os.path.join(
        dst_service,
        "src",
        "main",
        "resources"
    )

    os.makedirs(dst_resource, exist_ok=True)

    dst_file = os.path.join(dst_resource, "logback.xml")

    shutil.copy2(real_src, dst_file)
    COPIED.append(service_name)

print("=" * 60)
print("COPY XONG")
print("=" * 60)

print(f"\nĐã copy ({len(COPIED)} service):")
for x in COPIED:
    print("  ✔", x)

print(f"\nKhông có service tương ứng bên release ({len(SKIPPED)}):")
for x in SKIPPED:
    print("  -", x)

print(f"\nKhông tìm thấy logback bên Augmented ({len(NOT_FOUND)}):")
for x in NOT_FOUND:
    print("  -", x)