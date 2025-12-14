CLBTHOJ: CLB Tin Học Online Judge - Khoa Tin Học - UED
===

[![](https://github.com/DMOJ/online-judge/workflows/build/badge.svg)](https://lqdoj.edu.vn/)
[![Python](https://img.shields.io/pypi/pyversions/tensorflow.svg?style=plastic)](https://python.org)
[![OS](https://img.shields.io/badge/Ubuntu-16.04%20%7C%2018.04%20%7C%2020.04-brightgreen)](https://ubuntu.com/download)
[![License](https://img.shields.io/badge/license-AGPL--3.0-blue)](https://www.gnu.org/licenses/agpl-3.0.en.html)

## Overview

Homepage: [https://clbthoj.clbtinhocued.me](https://clbthoj.clbtinhocued.me)

Based on [DMOJ](https://dmoj.ca/).

Clone to [LQDOJ](https://lqdoj.edu.vn)

## Installation

- Bước 1: cài các thư viện cần thiết
    - $ ở đây nghĩa là sudo. Ví dụ dòng đầu nghĩa là chạy lệnh `sudo apt update`

```jsx
$ apt update
$ apt install git gcc g++ make python3-dev python3-pip libxml2-dev libxslt1-dev zlib1g-dev gettext curl redis-server
$ curl -sL https://deb.nodesource.com/setup_18.x | sudo -E bash -
$ apt install nodejs
$ npm install -g sass postcss-cli postcss autoprefixer
```

- Bước 2: tạo DB
    - Server đang dùng MariaDB ≥ 10.5, các bạn cũng có thể dùng Mysql nếu bị conflict
    - Nếu các bạn chạy lệnh dưới này xong mà version mariadb bị cũ (< 10.5) thì có thể tra google cách cài MariaDB mới nhất (10.5 hoặc 10.6).
    - Các bạn có thể thấy version MariaDB bằng cách gõ lệnh `sudo mysql` (Ctrl + C để quit)

```jsx
$ apt update
$ apt install mariadb-server libmysqlclient-dev
```

- Bước 3: tạo table trong DB
    - Các bạn có thể thay tên table và password

```jsx
$ sudo mysql
mariadb> CREATE DATABASE dmoj DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_general_ci;
mariadb> GRANT ALL PRIVILEGES ON dmoj.* TO 'dmoj'@'localhost' IDENTIFIED BY '<password>';
mariadb> exit
```

- Bước 4: Cài đặt môi trường ảo (virtual env) và pull code
    - Nếu `pip3 install mysqlclient` bị lỗi thì thử chạy `pip3 install mysqlclient==2.1.1`

```jsx
$ python3 -m venv clbthoj
$ . dmojsite/bin/activate

(clbthoj) $ git clone https://github.com/HoangNguynNe/CLBTH.git
(clbthoj) $ cd online-judge
(clbthoj) $ git submodule init
(clbthoj) $ git submodule update
(clbthoj) $ pip3 install -r requirements.txt
(clbthoj) $ pip3 install mysqlclient
(clbthoj) $ pre-commit install
```

- Bước 5: tạo local_settings.py. Đây là file để custom setting cho Django. Các bạn tạo file vào `online-judge/dmoj/local_settings.py`
    - File mẫu: https://github.com/DMOJ/docs/blob/master/sample_files/local_settings.py
    - Nếu bạn đổi tên hoặc mật khẩu table databases thì thay đổi thông tin tương ứng trong `Databases`
    - Sau khi xong, chạy lệnh `(dmojsite) $ python3 manage.py check` để kiểm tra
- Bước 6: Compile CSS và translation
    - Giải thích:
        - Lệnh 1 và 2 gọi sau mỗi lần thay đổi 1 file css hoặc file js (file html thì không cần)
        - Lệnh 3 và 4 gọi sau mỗi lần thay đổi file dịch
    - Note: Sau khi chạy lệnh này, folder tương ứng với STATIC_ROOT trong local_settings phải được tạo. Nếu chưa được tạo thì mình cần tạo folder đó trước khi chạy 2 lệnh đầu.

```jsx
(clbthoj) $ ./make_style.sh
(clbthoj) $ python3 manage.py collectstatic
(clbthoj) $ python3 manage.py compilemessages
(clbthoj) $ python3 manage.py compilejsi18n
```

- Bước 7: Thêm dữ liệu vào DB

```jsx
(clbthoj) $ python3 manage.py migrate
(clbthoj) $ python3 manage.py loaddata navbar
(clbthoj) $ python3 manage.py loaddata language_small
(clbthoj) $ python3 manage.py loaddata demo
```

- Bước 8: Chạy site. Đến đây thì cơ bản đã hoàn thành (chưa có judge, websocket, celery). Các bạn có thể truy cập tại `localhost:8000`

```jsx
python3 manage.py runserver 0.0.0.0:8000
```

**Một số lưu ý:**

1. (WSL) có thể tải ứng dụng Terminal trong Windows Store
2. (WSL) mỗi lần mở ubuntu, các bạn cần chạy lệnh sau để mariadb khởi động: `sudo service mysql restart` (tương tự cho một số service khác như memcached, celery)
3. Sau khi cài đặt, các bạn chỉ cần activate virtual env và chạy lệnh runserver là ok
```jsx
. dmojsite/bin/activate
python3 manage.py runserver
```
5. Đối với nginx, sau khi config xong theo guide của DMOJ, bạn cần thêm location như sau để sử dụng được tính năng profile image, thay thế `path/to/oj` thành đường dẫn nơi bạn đã clone source code.

```
location /profile_images/ {
    root /path/to/oj;
}
```

6. Quy trình dev:
    1. Sau khi thay đổi code thì django tự build lại, các bạn chỉ cần F5
    2. Một số style nằm trong các file .scss. Các bạn cần recompile css thì mới thấy được thay đổi.
