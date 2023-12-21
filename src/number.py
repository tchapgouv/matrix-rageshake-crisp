def number():
    for i in range(0, 1000):
        if i % 10 == 0:
            print(f'{i} {"*"*i} - DAPHNE')

if __name__ == "__main__":
    number()