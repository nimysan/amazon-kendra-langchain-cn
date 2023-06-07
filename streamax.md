# 如何构造

```bash
sudo apt update
sudo apt install software-properties-common

sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

sudo apt install python3.9

sudo apt install python3-pip
```

## 验证环境

python3 --version
alias python='python3'

## 测试

sudo pip3 install streamlit pgvector langchain

pip install pgvector #连接pgvector数据库

pip install -r requirements.txt #安装依赖包

## 安装pgvector驱动

```bash
sudo apt-get install libpq-dev
pip install psycopg2

```

## 安装PSQL环境驱动

```bash
sudo apt install postgresql-client-common   
sudo apt-get install postgresql-client

# 使用PSQL维护

ubuntu@ip-172-31-1-49:~/amazon-kendra-langchain-cn/pgsamples$ psql -h postgres.cypjqpec31mg.ap-southeast-1.rds.amazonaws.com -U postgres -d postgres -W
Password:
psql (14.8 (Ubuntu 14.8-0ubuntu0.22.04.1), server 15.2)
WARNING: psql major version 14, server major version 15.
         Some psql features might not work.
SSL connection (protocol: TLSv1.2, cipher: ECDHE-RSA-AES256-GCM-SHA384, bits: 256, compression: off)
Type "help" for help.

postgres=> CREATE EXTENSION vector;
CREATE EXTENSION
postgres=> SELECT typname FROM pg_type WHERE typname = 'vector';
 typname
---------
 vector
(1 row)
```

```sql
CREATE
EXTENSION vector;
SELECT typname
FROM pg_type
WHERE typname = 'vector';
```

## 问题

1. 如何抓取网页FAQ
2. 如何更新FAQ？（删除并更新）
3. 如何解决chatgpt token超出的问题？
4. 如何解决chatgpt输出慢的问题(--- 打字机 式输出)
5. 爬虫 远程机器不支持 selenium

```bash
selenium.common.exceptions.WebDriverException: Message: unknown error: cannot find Chrome binary
```

sudo apt-get install chromium-browser