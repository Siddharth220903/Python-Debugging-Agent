def add(a, b):
    return a + b

if __name__ == '__main__':
    try:
        result = add(5, 4)
    except TypeError as e:
        print(f'Error: {e}')
    else:
        print(f"Sum: {result}")