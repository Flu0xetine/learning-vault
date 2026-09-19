---
area: FastAPI
type: note
created: 2026-09-19
updated: 2026-09-19
related_daily:
  - "[[2026-09-19]]"
---

# Protocol 与接口兼容

## 本篇概览

`Protocol` 描述调用方需要的能力，使没有共同父类的对象也能在类型检查中满足同一个接口。本篇通过 Calculator、Storage 和模型替换示例，解释结构匹配、显式继承、方法完整性、参数名与类型兼容，以及 `...` 的含义。重点是“支持协议承诺的调用方式”，类型标注本身不会自动实施运行时校验。

## 学习来源

主要来源：[[2026-09-19#原始草稿]] 中的 Protocol 段落；会话补充了形参名称的追问、缺少方法的练习、运行时检查的误解和模型替换用途。草稿保留原文，下面明确纠正其参数改名示例的适用条件。先使用同步示例理解接口，不依赖异步知识。

## Protocol 描述对象需要具备什么能力

```python
from typing import Protocol

class Calculator(Protocol):
    def calculate(self, a: int, b: int) -> int:
        ...

class Adder:
    def calculate(self, a: int, b: int) -> int:
        return a + b

def run(calculator: Calculator) -> int:
    return calculator.calculate(1, 2)

print(run(Adder()))  # 3
```

`run()` 需要一个能以约定方式执行 `calculate` 的对象。`Adder` 没有继承 `Calculator`，但成员和签名兼容，因此类型检查器可以接受它。这称为结构化类型：根据对象提供的结构判断兼容性。

Protocol 不会将 Adder 转换成另一个类，也不会代替它计算。实际运行的仍然是 `Adder.calculate()`。

## 与普通继承的区别

普通类的名义类型关系通常依赖继承，例如 `class Dog(Animal)` 明确建立 Dog 与 Animal 的关系。Protocol 则允许没有该继承关系的类通过结构匹配满足接口。

也可以显式声明实现关系：

```python
class Adder(Calculator):
    def calculate(self, a: int, b: int) -> int:
        return a + b
```

这不是满足协议的必要条件，但能表达意图，并帮助类型检查器检查实现。Protocol 还可以提供默认实现；显式继承者可继承这些实现，只有结构匹配的类不会自动得到协议中的方法代码。

“普通类必须继承才能使用”不能作为 Python 运行时的普遍结论：普通 Python 函数也可能直接调用任何对象上存在的方法。这里比较的是类型系统如何确认接口兼容，而不是说不继承就必然无法运行。

## `...` 是什么

```python
class Calculator(Protocol):
    def calculate(self, a: int, b: int) -> int:
        ...
```

此处的 `...` 是代码中的真实占位写法，表示这里只声明接口，没有给出计算逻辑；它不是笔记删掉一段实现后的标记。实现类需要提供符合约定的行为。

在 Python 语法中，`...` 是 Ellipsis 字面量。把它单独放进函数体不会自动抛出“尚未实现”异常，也不会自动产生符合返回标注的结果。普通函数若只有这一句，运行到末尾会隐式返回 None。因此不能依靠占位方法完成业务，也不能把它理解成运行时强制检查机制。

## 重点疑问：形参名称可以不同吗

**当时的问题**：既然方法参数类型相同，形参名字不必相同，对吗？

草稿示例将原协议的 `a, b` 改为 `x, y`：

```python
class RenamedAdder:
    def calculate(self, x: int, y: int) -> int:
        return x + y
```

这个对象能执行 `calculate(1, 2)`，但协议中的普通参数还允许关键字调用：

```python
def run_named(calculator: Calculator) -> int:
    return calculator.calculate(a=1, b=2)
```

若传入 RenamedAdder，Python 会因不认识关键字 `a`、`b` 而报 TypeError。因此，“位置调用能成功”不足以证明符合整个协议。对原草稿的 Calculator 而言，改名的实现不兼容。

### 什么情况下名字可以不同

以下为补充说明，用来交代“调用方式兼容”的边界：

```python
class PositionalCalculator(Protocol):
    def calculate(self, a: int, b: int, /) -> int:
        ...

def run_positional(calculator: PositionalCalculator) -> int:
    return calculator.calculate(1, 2)
```

`/` 前面的参数是仅位置参数，调用方不能依据这个协议写 `a=1, b=2`。上面的 RenamedAdder 能接受协议承诺的位置调用，因此可匹配这个版本的协议；实现额外允许 `x=...`、`y=...` 不影响兼容。

初学时保持参数名、类型和返回类型一致最直接；真正的规则是实现能接受协议允许的调用，并提供兼容结果，而不是要求源码逐字相同。

## 方法名相同还不够

```python
class Converter(Protocol):
    def convert(self, value: str) -> int:
        ...

class ConverterA:
    def convert(self, value: str) -> int:
        return int(value)

class ConverterB:
    def convert(self, value: int) -> str:
        return str(value)
```

会话中选择 A 正确：它接受协议要求的字符串，返回整数。B 接受整数并返回字符串，不能承担同样的调用约定。

类型兼容也不是类型名称必须完全相同：实现可以接受更广的输入，并返回满足协议要求的结果。例如协议接受 str，实现接受 object 且正确处理这些输入，也可能兼容。当前阶段无需展开泛型与变型，但应避免把“相同签名是简单可靠的写法”误记为唯一合法写法。

## 多个方法必须完整提供

```python
class Storage(Protocol):
    def save(self, key: str, value: str) -> None:
        ...

    def load(self, key: str) -> str:
        ...

class MemoryStorage:
    def __init__(self) -> None:
        self.data: dict[str, str] = {}

    def save(self, key: str, value: str) -> None:
        self.data[key] = value

    def load(self, key: str) -> str:
        return self.data[key]
```

MemoryStorage 同时实现 save 和 load。会话中的 ReadOnlyStorage 只有 load，缺少 save，因此不完整符合 Storage。对象可以有额外能力，但不能缺少协议要求的成员。

## 类型检查与运行时行为

```python
class ReadOnlyStorage:
    def load(self, key: str) -> str:
        return "value"

def store_value(storage: Storage) -> None:
    storage.save("name", "Alice")
```

`store_value(ReadOnlyStorage())` 应被静态类型检查器指出不兼容。若跳过类型检查直接运行，Python 不会因为参数标注为 Storage 就在函数入口自动验证协议，而是在执行 `.save()` 时因缺少方法产生 AttributeError。

同理，Protocol 不会自动转换参数、验证返回值或保证业务正确。默认也不能把普通 Protocol 直接用于 `isinstance()`；即便额外使用 `@runtime_checkable`，其运行时成员检查也不等于完整的参数和返回类型校验。本篇使用静态接口约定即可。

## Agent 中的用途：替换模型实现

```python
class ChatModel(Protocol):
    def generate(self, prompt: str) -> str:
        ...

class FakeModel:
    def generate(self, prompt: str) -> str:
        return f"测试回答：{prompt}"

def answer_question(model: ChatModel, question: str) -> str:
    return model.generate(question)

print(answer_question(FakeModel(), "什么是 FastAPI？"))
```

业务函数依赖 generate 能力。测试时注入 FakeModel，不需要网络或模型费用；正式实现可以在同名方法中调用真实客户端。若某个 SDK 的方法名称或调用方式不同，需要自己写一个适配类，不能假设所有厂商对象天然满足此协议。

协议名称或实现类叫 RealModel，并不意味着代码真的访问了模型；会话中返回固定字符串的例子仍是模拟实现。适合采用 Protocol 的场景是调用方只需要稳定的一组能力、希望替换具体实现，而不是每个类都必须套一层协议。

## 复习自测

1. Adder 为什么不继承 Calculator 也能满足协议？——其必需方法及调用签名结构兼容。
2. `calculate(x, y)` 能接受 `(1, 2)`，为何仍不满足原协议？——还必须支持原协议允许的 `a=...`、`b=...`。
3. 如何允许实现使用不同参数名？——若接口设计只需要位置调用，可以在协议中将相应参数声明为仅位置参数。
4. `...` 是未展示的算法吗？——不是，它在这里是接口占位，未提供业务算法。
5. 只有 load 的对象能作为 Storage 吗？——不能，还缺少 save。
6. 标注 Storage 会在函数入口自动拒绝错误对象吗？——不会；静态检查与运行时执行分开。
7. 何时使用 Protocol？——希望调用方依赖能力、能替换不同实现或测试替身时。

## 官方参考

- [Python 类型规范：Protocols](https://typing.python.org/en/latest/spec/protocol.html)
- [Python 类型规范：可调用对象与参数兼容](https://typing.python.org/en/latest/spec/callables.html)

---

下一篇：暂无
