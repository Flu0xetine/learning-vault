def calculate(text: str, divisor: int):

    #  1.try:finally: 解决的问题：无论程序正常结束还是发生异常，都要释放资源。
    try:
        number = int(text)
        result = number / divisor
        print("计算结果：", result)
    # 2.1 except 捕获异常并处理后不会返回 try 继续执行，所以通常只会捕获一次异常
    except ValueError as error:
        print("无法转换成整数")
        print("异常信息：", error)

    except ZeroDivisionError:
        print("除数不能为零")
    # 2.2 发生异常，但没有匹配的 except 不执行 else，直接执行 finally
    # 2.3 else 没有发生异常时执行，最终也会执行 finally
    else:
        print("success")
    # 3.finally 执行释放资源类代码，必须跟在 try 后面不能单独出现
    finally:
        print("本次计算结束")

calculate("99",0)
print("====")
calculate("9k9",2)

