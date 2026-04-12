import subprocess
import json
import string
import time

MAX_RETRY = 10

def run_cmd(cmd, timeout=None):
    """اجرای دستور با تایم‌اوت و بازگرداندن خروجی"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            text=True
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return None


def expect_json(output, required_keys):
    """چک می‌کند خروجی شامل JSON درست با کلیدهای مورد انتظار هست یا نه"""
    if not output:
        return False
    try:
        data = json.loads(output)
        pointer = data
        for key in required_keys:
            if key not in pointer:
                return False
            pointer = pointer[key]
        return True
    except:
        return False


def upload_part(part_file, upload_url):
    """اجرای مرحله آپلود (curl)"""
    cmd = f'curl -X POST "{upload_url}" -F "file=@{part_file}"'
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=120,   # مرحله ۲ → تا ۲ دقیقه
            text=True
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return None



def get_letter_pairs(n):
    """تولید نام پارت مثل aa, ab, ac ..."""
    letters = string.ascii_lowercase
    out = []
    for i in range(n):
        a = letters[i // 26]
        b = letters[i % 26]
        out.append(a + b)
    return out


def main():
    try:
        count = int(input("تعداد پارت‌ها را وارد کنید: "))
    except:
        print("عدد صحیح وارد کن")
        return

    part_names = get_letter_pairs(count)

    for idx, part in enumerate(part_names):
        print(f"\n--- پردازش پارت {idx+1}/{count} : part_{part} ---")

        # ---- مرحله 1 ----
        print("مرحله 1: اجرای python3 testrubica.py ...")
        for attempt in range(MAX_RETRY):
            out = run_cmd("python3 testrubica.py", timeout=3)
            if expect_json(out, ["status", "data"]):
            # خروجی باید فرم { "upload_url": "..." } داخل data باشد
                try:
                    upload_url = json.loads(out)["data"]["upload_url"]
                    print("OK → upload_url:", upload_url)
                    break
                except:
                    pass
            print("خطا در مرحله 1 → تلاش مجدد", attempt+1)
            time.sleep(1)
        else:
            print("مرحله 1 بعد از ۱۰ تلاش شکست خورد")
            return
        
        # ---- مرحله 2 ----
        print("مرحله 2: آپلود پارت با curl ...")
        part_file = f"part_{part}"
        for attempt in range(MAX_RETRY):
            out = upload_part(part_file, upload_url)
            if expect_json(out, ["status", "data"]):
                try:
                    file_id = json.loads(out)["data"]["file_id"]
                    print("OK → file_id:", file_id)
                    break
                except:
                    pass
            print("خطا در مرحله 2 → تلاش مجدد", attempt+1)
            time.sleep(2)
        else:
            print("مرحله 2 بعد از ۱۰ تلاش شکست خورد")
            return

        # ---- مرحله 3 ----
        print("مرحله 3: اجرای send.sh ...")
        for attempt in range(MAX_RETRY):
            out = run_cmd("./send.sh", timeout=3)
            if expect_json(out, ["status", "data"]):
                try:
                    message_id = json.loads(out)["data"]["message_id"]
                    print("OK → message_id:", message_id)
                    break
                except:
                    pass
            print("خطا در مرحله 3 → تلاش مجدد", attempt+1)
            time.sleep(1)
        else:
            print("مرحله 3 بعد از ۱۰ تلاش شکست خورد")
            return

        print(f"پارت {part} با موفقیت کامل شد.\n")


if __name__ == "__main__":
    main()
`
