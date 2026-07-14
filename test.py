import math

from precise_number import PreciseNumber as pn
pn.float_value_warning = False
p = pn(-0.153)
b = pn(0.23)
c = pn(-0.2)
d = pn(0.1)
e = pn(-0.1)
f = pn(-0.13)
g = pn(2)
h = pn(0.5)
i = pn('11')
j = pn('0.3')

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
        print('floor:',math.floor(obj))
        print('ceil:', math.ceil(obj))
        try:
            print('ln:',  obj.ln())
        except ValueError:
            print('ln: impossible')
        print('exp:', obj.exp())
        try:
            print('pow:', obj ** obj2)
        except ValueError:
            print('pow: impossible')

print(pn.PI + 1)
