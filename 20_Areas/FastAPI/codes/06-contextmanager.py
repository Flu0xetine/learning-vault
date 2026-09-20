# 类写法：我们可以自定义类时
# class DatabaseConnection:
#     def __enter__(self):
#         print("连接数据库")
#         return self

#     def query(self):
#         print("查询数据")

#     def __exit__(self, exc_type, exc_value, traceback):
#         print("关闭数据库连接")
#         return False
# with DatabaseConnection() as db:
#     db.query()

# @contextmanager 写法：有时资源对象不是我们写的，或者我们只想包装一小段获取和释放逻辑。
# 来自第三方库，我们不方便修改它的类，也不能直接给它添加 __enter__ 和 __exit__。
from contextlib import contextmanager
class Connection:
    def query(self):
        print("查询数据库")

    def close(self):
        print("关闭数据库连接")
class third_party_library:
    @staticmethod
    def connect():
        print("连接数据库")
        return Connection()

@contextmanager 
# 相当于告诉 Python：请把这个以 yield 为分界线的生成器，包装成一个具有 __enter__ 和 __exit__ 的对象。 
# 从而可以把它放进 with ... as 里
def database_connection():
     # 第一部分：进入 with 时执行
    connection = third_party_library.connect()
    try:
        yield connection
        # yield 的值交给 as 后面的变量
    finally:
        # 第二部分：离开 with 时执行
        connection.close()

with database_connection() as connection:
    connection.query()