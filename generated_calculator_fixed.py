import re

class Calculator:
    def __init__(self):
        self.expression = ""

    def add_number(self, number):
        self.expression += str(number)

    def add_operator(self, operator):
        self.expression += operator

    def calculate(self):
        # 修复正则表达式的 bug
        pattern = r'(\d+)([+\-*/])(\d+)'
        matches = re.findall(pattern, self.expression)

        result = 0
        for match in matches:
            num1, operator, num2 = match
            num1, num2 = int(num1), int(num2)

            if operator == '+':
                result += num2
            elif operator == '-':
                result -= num2
            elif operator == '*':
                result *= num2
            elif operator == '/':
                result /= num2

        return result

# 测试代码
calc = Calculator()
calc.add_number(10)
calc.add_operator('-')
calc.add_number(2)
print(calc.calculate())