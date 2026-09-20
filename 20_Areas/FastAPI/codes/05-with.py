def test0():
    manager = open("example.txt")
    file = manager.__enter__()

    try:
        content = file.read() # 执行
    finally:
        manager.__exit__(...)

def main():
    # 1.with 封装 三步: 赋值(enter) -> try(执行) -> finally(exit)
    with open("example.txt") as file:
        content = file.read() # 执行
    # 2.等价于 test0()
    # 一个对象想要支持 with，需要实现：
    # 2.1__enter__() 进入上下文，return 的值会赋给 as 后的变量
    # 2.2__exit__() 退出上下文，释放资源。 

    # 2.2.1 exit参数如下：如果 with 正常结束，三者都是 None
    # exc_type：异常类型，例如 ValueError
    # exc_value：异常对象，例如 ValueError("操作失败")
    # traceback：异常调用栈

    # 2.2.2 返回值： return bool|None
    # True:抑制异常不向外传播，可用 return exc_type is ValueError 专门抑制 ValueError 类型的异常
    # False or None: 继续向外传播异常

    # 向外传播：沿函数调用关系传播
    # def inner():
    #     raise ValueError("出错了")


    # def outer():
    #     try:
    #         inner()
    #     except ValueError as error:
    #         print("outer 捕获异常：", error)


    # outer()
    # print("程序继续运行")



main()