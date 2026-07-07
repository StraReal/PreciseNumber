max_decimal_precision = 20

class PreciseNumber:
    def __init__(self, value: int | float, nexp: int = 0):
        self.value = None
        self.nexp = None
        self.precise = True
        self.set(value, nexp)

    def set(self, value: int | float, nexp: int = 0):
        if value == 0:
            self.value = 0
            self.nexp = 0
            return
        if type(value) == int:
            v = str(abs(value))
            trim = min(nexp, len(v) - len(v.rstrip('0')))
            self.value = value // 10 ** trim if trim else value
            self.nexp = nexp - trim
        else:
            v = str(value)
            v = v.split('.')
            self.nexp = len(v[1]) + nexp
            self.nexp -= len(v[1]) - len(v[1].rstrip('0'))
            v[1] = v[1].rstrip('0')
            v = v[0] + v[1]
            self.value = int(v)

        if self.nexp > max_decimal_precision:
            excess = self.nexp - max_decimal_precision
            sign = -1 if self.value < 0 else 1
            self.value = sign * (abs(self.value) // 10 ** excess)
            self.nexp = max_decimal_precision
            self.precise = False
            # re-trim any trailing zeros exposed by truncation
            if self.value != 0:
                v = str(abs(self.value))
                trim = min(self.nexp, len(v) - len(v.rstrip('0')))
                if trim:
                    self.value //= 10 ** trim
                    self.nexp -= trim
            else:
                self.nexp = 0

    def __round__(self, ndigits: int):
        if self.nexp <= ndigits:
            result = PreciseNumber(self.value, self.nexp)
            result.precise = result.precise and self.precise
            return result
        if ndigits < 0:
            raise ValueError('negative ndigits not supported (nexp cannot go below 0)')

        drop = self.nexp - ndigits
        sign = -1 if self.value < 0 else 1
        av = abs(self.value)
        divisor = 10 ** drop
        quotient, remainder = divmod(av, divisor)
        if remainder * 2 >= divisor:  # round half up
            quotient += 1
        result = PreciseNumber(sign * quotient, ndigits)
        result.precise = result.precise and self.precise
        return result

    def __eq__(self, other: 'PreciseNumber'):
        return self.value == other.value and self.nexp == other.nexp


    def __lt__(self, other: 'PreciseNumber'):
        if self.nexp == other.nexp:
            return self.value < other.value
        elif self.nexp > other.nexp:
            o = int(str(other.value) + '0' * (self.nexp - other.nexp))
            return self.value < o
        else:
            v = int(str(self.value) + '0' * (other.nexp - self.nexp))
            return v < other.value


    def __gt__(self, other: 'PreciseNumber'):
        if self.nexp == other.nexp:
            return self.value > other.value
        elif self.nexp > other.nexp:
            o = int(str(other.value) + '0' * (self.nexp - other.nexp))
            return self.value > o
        else:
            v = int(str(self.value) + '0' * (other.nexp - self.nexp))
            return v > other.value

    def __add__(self, other):
        if self.nexp == other.nexp:
            result = PreciseNumber(self.value + other.value, self.nexp)
        elif self.nexp > other.nexp:
            o = str(other.value) + '0' * (self.nexp - other.nexp)
            result = PreciseNumber(int(o) + self.value, self.nexp)
        else:
            v = str(self.value) + '0' * (other.nexp - self.nexp)
            result = PreciseNumber(int(v) + other.value, other.nexp)
        result.precise = result.precise and self.precise and other.precise
        return result

    def __neg__(self):
        result = PreciseNumber(-self.value, self.nexp)
        result.precise = result.precise and self.precise
        return result

    def __mul__(self, other):
        result = PreciseNumber(self.value * other.value, self.nexp + other.nexp)
        result.precise = result.precise and self.precise and other.precise
        return result

    def __sub__(self, other):
        return self + (-other)

    def __truediv__(self, other):
        if other.value == 0:
            raise ZeroDivisionError("division by zero")

        sign = -1 if (self.value < 0) != (other.value < 0) else 1
        a, b = abs(self.value), abs(other.value)

        result_nexp = self.nexp - other.nexp + max_decimal_precision
        quotient, remainder = divmod(a * 10 ** max_decimal_precision, b)
        exact = remainder == 0

        result = PreciseNumber(sign * quotient, result_nexp)
        result.precise = result.precise and self.precise and other.precise and exact
        return result

    def __str__(self):
        if self.nexp:
            neg = self.value < 0
            s = str(abs(self.value))
            s = '0' * (self.nexp - len(s) + 1) + s
            split = len(s) - self.nexp
            result = s[:split] + '.' + s[split:]
            return '-' + result if neg else result
        else:
            return str(self.value)

    def get(self):
        if self.nexp <= 0:
            return int(str(self))
        else:
            return float(str(self))