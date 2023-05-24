from faker import Faker
fake = Faker()
from app import app
import urllib3
from Process_Recipe import process_recipe
from Process_User import process_user


if __name__ == "__main__":
    # 取消http警告
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    url = "https://home.meishichina.com/space-10667631.html"
    with app.app_context():
        process_user(url)

