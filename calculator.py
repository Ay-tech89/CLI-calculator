import ast
import operator
import os
from decimal import Decimal, getcontext, DivisionByZero, InvalidOperation

getcontext().prec = 28

class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

# Mapping AST nodes to math operations
operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def safe_eval(node):
    """Recursively evaluates the parsed AST to prevent code injection."""
    if isinstance(node, ast.Expression):
        return safe_eval(node.body)
    elif isinstance(node, ast.Constant): 
        if isinstance(node.value, (int, float)):
            return Decimal(str(node.value))
        raise ValueError("Unsupported constant")
    elif isinstance(node, ast.Num):
        return Decimal(str(node.n))
    elif isinstance(node, ast.BinOp):
        op = type(node.op)
        if op not in operators:
            raise ValueError(f"Unsupported operator: {op.__name__}")
        left = safe_eval(node.left)
        right = safe_eval(node.right)
        if op == ast.Div and right == Decimal(0):
            raise ZeroDivisionError("Division by zero is not allowed.")
        return operators[op](left, right)
    elif isinstance(node, ast.UnaryOp):
        op = type(node.op)
        if op not in operators:
            raise ValueError(f"Unsupported operator: {op.__name__}")
        operand = safe_eval(node.operand)
        return operators[op](operand)
    elif isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only simple function calls are allowed")
        func_name = node.func.id
        if func_name == 'sqrt':
            args = [safe_eval(arg) for arg in node.args]
            if len(args) != 1:
                raise ValueError("sqrt takes exactly 1 argument")
            if args[0] < 0:
                raise ValueError("Cannot calculate square root of a negative number")
            return args[0].sqrt()
        else:
            raise ValueError(f"Unsupported function: {func_name}")
    elif isinstance(node, ast.Name):
        # Support constants
        if node.id == 'pi':
            return Decimal('3.141592653589793238462643383')
        if node.id == 'e':
            return Decimal('2.718281828459045235360287471')
        raise ValueError(f"Unknown variable: {node.id}")
    else:
        raise ValueError("Unsupported expression structure")

def evaluate_expression(expr_str):
    expr_str = expr_str.replace('^', '**')
    try:
        tree = ast.parse(expr_str, mode='eval')
    except SyntaxError:
        raise ValueError("Invalid mathematical expression syntax")
    
    return safe_eval(tree)

def format_result(val):
    # Normalize removes trailing zeros, to_integral_value checks if it's an integer
    val = val.normalize()
    if val == val.to_integral_value():
        return str(int(val))
    return str(val)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_welcome():
    print(f"{Color.CYAN}========================================={Color.RESET}")
    print(f"{Color.CYAN}               CLI Calculator            {Color.RESET}")
    print(f"{Color.CYAN}========================================={Color.RESET}")
    print(f"Modes:")
    print(f"  - String Expr: Type your equation (e.g., (10 + 5) * 2)")
    print(f"  - Step-by-Step: Type 'step' to enter step-by-step mode")
    print(f"Commands:")
    print(f"  'clear' - Clear the terminal history")
    print(f"  'quit'  - Exit the calculator")
    print(f"{Color.CYAN}========================================={Color.RESET}")

def run_step_by_step():
    print(f"\n{Color.CYAN}--- Step-by-Step Mode ---{Color.RESET}")
    print(f"(Type 'cancel' at any prompt to return to the main menu)")
    
    # Get Number 1
    num1_str = input(f"{Color.YELLOW}Number 1: {Color.RESET}").strip()
    if num1_str.lower() == 'cancel': return
    try:
        num1 = Decimal(num1_str)
    except Exception:
        print(f"{Color.RED}Error: Invalid number format. Expected a numeric value.{Color.RESET}")
        return
        
    # Get Operator
    op = input(f"{Color.YELLOW}Operator (+, -, *, /, ^, %, sqrt): {Color.RESET}").strip()
    if op.lower() == 'cancel': return
    
    if op == 'sqrt':
        if num1 < 0:
            print(f"{Color.RED}Error: Cannot calculate square root of a negative number.{Color.RESET}")
        else:
            print(f"{Color.GREEN}= {format_result(num1.sqrt())}{Color.RESET}")
        return
        
    if op not in ['+', '-', '*', '/', '^', '%']:
        print(f"{Color.RED}Error: Invalid operator. Supported operators: +, -, *, /, ^, %, sqrt.{Color.RESET}")
        return
        
    # Get Number 2
    num2_str = input(f"{Color.YELLOW}Number 2: {Color.RESET}").strip()
    if num2_str.lower() == 'cancel': return
    try:
        num2 = Decimal(num2_str)
    except Exception:
        print(f"{Color.RED}Error: Invalid number format. Expected a numeric value.{Color.RESET}")
        return
 
    try:
        if op == '+': res = num1 + num2
        elif op == '-': res = num1 - num2
        elif op == '*': res = num1 * num2
        elif op == '/': 
            if num2 == 0:
                raise ZeroDivisionError("Division by zero is not allowed.")
            res = num1 / num2
        elif op == '^': 
            res = num1 ** num2
        elif op == '%': res = num1 % num2
        
        print(f"{Color.GREEN}= {format_result(res)}{Color.RESET}")
    except InvalidOperation:
        print(f"{Color.RED}Error: Invalid mathematical operation.{Color.RESET}")
    except Exception as e:
        print(f"{Color.RED}Error: {e}{Color.RESET}")

def main():
    if os.name == 'nt':
        os.system('')
    
    clear_screen()
    print_welcome()
    
    while True:
        try:
            user_input = input(f"\n{Color.YELLOW}calc > {Color.RESET}").strip()
            
            if not user_input:
                continue
                
            cmd = user_input.lower()
            if cmd in ('quit', 'exit', 'q'):
                print(f"{Color.GREEN}Goodbye!{Color.RESET}")
                break
            elif cmd == 'clear':
                clear_screen()
                print_welcome()
                continue
            elif cmd == 'step':
                run_step_by_step()
                continue
            
            result = evaluate_expression(user_input)
            print(f"{Color.GREEN}= {format_result(result)}{Color.RESET}")
            
        except KeyboardInterrupt:
            print(f"\n{Color.GREEN}Goodbye!{Color.RESET}")
            break
        except EOFError:
            print(f"\n{Color.GREEN}Goodbye!{Color.RESET}")
            break
        except ZeroDivisionError as e:
            print(f"{Color.RED}Error: {e}{Color.RESET}")
        except ValueError as e:
            print(f"{Color.RED}Error: {e}{Color.RESET}")
        except InvalidOperation:
            print(f"{Color.RED}Error: Invalid mathematical operation.{Color.RESET}")
        except Exception as e:
            print(f"{Color.RED}Error: Unexpected error occurred: {e}{Color.RESET}")

if __name__ == "__main__":
    main()
