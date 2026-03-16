#!/usr/bin/env python3
"""
AutoDev 生成的计算器程序示例

这是 AutoDev 系统自动生成的代码示例
"""

class Calculator:
    """简单的计算器类"""

    def add(self, a, b):
        """加法"""
        return a + b

    def subtract(self, a, b):
        """减法"""
        return a - b

    def multiply(self, a, b):
        """乘法"""
        return a * b

    def divide(self, a, b):
        """除法"""
        if b == 0:
            raise ValueError("除数不能为零")
        return a / b

    def calculate(self, expression):
        """
        计算表达式

        支持格式: "数字 运算符 数字"
        例如: "5 + 3", "10 / 2"
        """
        try:
            parts = expression.strip().split()
            if len(parts) != 3:
                raise ValueError("格式错误，请使用: 数字 运算符 数字")

            num1 = float(parts[0])
            operator = parts[1]
            num2 = float(parts[2])

            if operator == '+':
                return self.add(num1, num2)
            elif operator == '-':
                return self.subtract(num1, num2)
            elif operator == '*':
                return self.multiply(num1, num2)
            elif operator == '/':
                return self.divide(num1, num2)
            else:
                raise ValueError(f"不支持的运算符: {operator}")

        except ValueError as e:
            raise ValueError(f"输入错误: {e}")
        except Exception as e:
            raise Exception(f"计算失败: {e}")


def main():
    """命令行界面"""
    calc = Calculator()

    print("=" * 50)
    print("简单计算器")
    print("=" * 50)
    print("支持的运算: + - * /")
    print("格式: 数字 运算符 数字")
    print("输入 'quit' 退出")
    print("=" * 50)

    while True:
        try:
            expression = input("\n请输入表达式: ").strip()

            if expression.lower() in ['quit', 'exit', 'q']:
                print("再见！")
                break

            if not expression:
                continue

            result = calc.calculate(expression)
            print(f"结果: {result}")

        except ValueError as e:
            print(f"错误: {e}")
        except Exception as e:
            print(f"错误: {e}")


if __name__ == "__main__":
    main()
