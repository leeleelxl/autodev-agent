import re
import sys

def input_parser(expression):
    # 使用正则表达式匹配数字和操作符
    numbers = re.findall(r'-?\d+', expression)
    operators = re.findall(r'[*/+-]', expression)
    # 验证输入格式是否正确
    if len(numbers) - len(operators) != 1:
        raise ValueError("Invalid input format. Each operator must be between two numbers.")
    return numbers, operators

def calculate(numbers, operators):
    result = int(numbers[0])
    for operator, next_number in zip(operators, numbers[1:]):
        if operator == "+":
            result += int(next_number)
        elif operator == "-":
            result -= int(next_number)
        elif operator == "*":
            result *= int(next_number)
        elif operator == "/":
            if int(next_number) == 0:
                raise ZeroDivisionError("Cannot divide by zero.")
            result /= int(next_number)
    return result

def error_handler():
    while True:
        try:
            return input("Enter your mathematical expression (or 'exit' to quit): ").strip()
        except ValueError as e:
            print(f"Error: {e}")
        except ZeroDivisionError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

def display_result(result):
    print(f"Result: {result}")

def main():
    while True:
        expression = error_handler()
        if expression.lower() == 'exit':
            break
        try:
            numbers, operators = input_parser(expression)
            result = calculate(numbers, operators)
            display_result(result)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()