from precise_number import PreciseNumber
p = PreciseNumber(-0.153)
b = PreciseNumber(0.23)
c = PreciseNumber(-0.2)
d = PreciseNumber(0.1)
e = PreciseNumber(-0.1)
f = PreciseNumber(-0.13)
g = PreciseNumber(2)
h = PreciseNumber(0.5)
i = PreciseNumber('11')
j = PreciseNumber('0.3')

objs = [p, b, c, d, e, f, g, h]
for obj in objs:
    for obj2 in objs:
        print()
        print(f'= | {obj} | {obj2} | =')
        print('eq:',  obj ==obj2)
        print('lt:',  obj < obj2)
        print('gt:',  obj > obj2)
        print('add:', obj + obj2)
        print('sub:', obj - obj2)
        print('mul:', obj * obj2)
        print('div:', obj / obj2)
        try:
            print('ln:',  obj.ln())
        except ValueError:
            print('ln: impossible')
        print('exp:', obj.exp())
        try:
            print('pow:', obj ** obj2)
        except ValueError:
            print('pow: impossible')