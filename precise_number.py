import warnings

class PreciseNumber:
    max_decimal_precision = 28
    float_value_warning = True

    def __init__(self, value: int | float | str, nexp: int = 0, precise: bool = True):
        self.value = None
        self.nexp = None
        self.precise = precise
        self.set(value, nexp)

    def set(self, value: int | float | str, nexp: int = 0):
        if value == 0:
            self.value = 0
            self.nexp = 0
            return
        if isinstance(value, int):
            v = str(abs(value))
            trim = min(nexp, len(v) - len(v.rstrip('0')))
            self.value = value // 10 ** trim if trim else value
            self.nexp = nexp - trim
        else:
            if isinstance(value, float) and self.float_value_warning:
                warnings.warn(
                    "Constructing PreciseNumber from a float may inherit floating-point imprecision.\n"
                    "Consider using a string (e.g. '0.1') or an int instead.\n"
                    f"Given float: {value!r}",
                    UserWarning,
                    stacklevel=2,
                )
            v = str(value)
            if "." not in v:
                v += ".0"
            v = v.split('.')
            self.nexp = len(v[1]) + nexp
            self.nexp -= len(v[1]) - len(v[1].rstrip('0'))
            v[1] = v[1].rstrip('0')
            v = v[0] + v[1]
            self.value = int(v)

        if self.nexp > self.max_decimal_precision:
            excess = self.nexp - self.max_decimal_precision
            sign = -1 if self.value < 0 else 1
            self.value = sign * (abs(self.value) // 10 ** excess)
            self.nexp = self.max_decimal_precision
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

    @staticmethod
    def _coerce(value):
        if isinstance(value, PreciseNumber):
            return value
        result = PreciseNumber.__new__(PreciseNumber)
        result.precise = True
        result.set(value)
        return result

    def exp(self):
        # e^x using Taylor series: e^x = 1 + x + x^2/2! + x^3/3! + ..
        result = PreciseNumber(1)
        term = PreciseNumber(1)
        for i in range(1, self.max_decimal_precision + 50):
            term = term * self / PreciseNumber(i)
            result = result + term
            # Stop when term is negligibly small
            if term.nexp > 0 and abs(term.value) < 1:
                break
        return result

    def ln(self):
        if self.value <= 0:
            raise ValueError("ln only defined for positive numbers")

        # Use series: ln(x) = 2 * sum_{n=0}^∞ (1/(2n+1)) * ((x-1)/(x+1))^(2n+1)
        x_minus_1 = self - PreciseNumber(1)
        x_plus_1 = self + PreciseNumber(1)

        y = x_minus_1 / x_plus_1  # (x-1)/(x+1)

        result = PreciseNumber(0)
        term = y
        for n in range(self.max_decimal_precision + 50):
            result = result + term / PreciseNumber(2 * n + 1)
            term = term * y * y  # y^(2n+3)
            if term.nexp > 0 and abs(term.value) < 1:
                break

        return PreciseNumber(2) * result

    def __repr__(self):
        return str(self)

    def __index__(self):
        if self.nexp <= 0:
            return self.value * (10 ** -self.nexp)
        quotient, remainder = divmod(self.value, 10 ** self.nexp)
        if remainder:
            raise TypeError("PreciseNumber is not integral")
        return quotient

    def __pow__(self, exponent):
        exponent = self._coerce(exponent)

        # Check if exponent is 0
        if exponent.value == 0 and exponent.nexp == 0:
            return PreciseNumber(1)

        # Check if exponent is 1
        if exponent.value == 1 and exponent.nexp == 0:
            result = PreciseNumber(self.value, self.nexp)
            result.precise = self.precise
            return result

        # Check if integer exponent (no decimal places)
        is_integer = exponent.nexp == 0

        if is_integer:
            # int exp (exact)
            exp_int = exponent.value
            if exp_int < 0:
                return PreciseNumber(1) / (self ** PreciseNumber(-exp_int))

            new_value = self.value ** exp_int
            new_nexp = self.nexp * exp_int
            result = PreciseNumber.__new__(PreciseNumber)
            result.value = new_value
            result.nexp = new_nexp
            result.precise = self.precise

            if new_nexp > self.max_decimal_precision:
                excess = new_nexp - self.max_decimal_precision
                result.value //= 10 ** excess
                result.nexp = self.max_decimal_precision
                result.precise = False

            return result
        else:
            # fractional ( n^x = e^(x * ln(n)) )
            if self.value <= 0:
                raise ValueError("fractional exponents only defined for positive numbers")

            result = (exponent * self.ln()).exp()
            result.precise = False
            return result

    def __abs__(self):
        return self if self.value > 0 else -self

    def __round__(self, ndigits: int = 0):
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

    def _cmp(self, other):
        other = self._coerce(other)
        a, b = self.value, other.value
        sa = (a > 0) - (a < 0)
        sb = (b > 0) - (b < 0)
        if sa != sb:
            return (sa > sb) - (sa < sb)

        if self.nexp > other.nexp:
            b *= 10 ** (self.nexp - other.nexp)
        elif self.nexp < other.nexp:
            a *= 10 ** (other.nexp - self.nexp)

        return (a > b) - (a < b)

    def __floor__(self):
        if self.nexp <= 0:
            return self.value * (10 ** (-self.nexp))
        else:
            return self.value // (10 ** self.nexp)

    def __ceil__(self):
        if self.nexp <= 0:
            return self.value * (10 ** (-self.nexp))
        else:
            divisor = 10 ** self.nexp
            return -(-self.value // divisor)

    def __lt__(self, other):
        return self._cmp(other) < 0

    def __le__(self, other):
        return self._cmp(other) <= 0

    def __gt__(self, other):
        return self._cmp(other) > 0

    def __ge__(self, other):
        return self._cmp(other) >= 0

    def __eq__(self, other):
        return self._cmp(other) == 0

    def __hash__(self):
        return hash(str(self))

    def __add__(self, other):
        other = self._coerce(other)
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
        other = self._coerce(other)
        result = PreciseNumber(self.value * other.value, self.nexp + other.nexp)
        result.precise = result.precise and self.precise and other.precise
        return result

    def __sub__(self, other):
        other = self._coerce(other)
        return self + (-other)

    def __truediv__(self, other):
        other = self._coerce(other)
        if other.value == 0:
            raise ZeroDivisionError("division by zero")

        sign = -1 if (self.value < 0) != (other.value < 0) else 1
        a, b = abs(self.value), abs(other.value)

        result_nexp = self.nexp - other.nexp + self.max_decimal_precision
        quotient, remainder = divmod(a * 10 ** self.max_decimal_precision, b)
        exact = remainder == 0

        result = PreciseNumber(sign * quotient, result_nexp)
        result.precise = result.precise and self.precise and other.precise and exact
        return result

    def __floordiv__(self, other):
        other = self._coerce(other)
        if other.value == 0:
            raise ZeroDivisionError("division by zero")

        sign = -1 if (self.value < 0) != (other.value < 0) else 1
        a, b = abs(self.value), abs(other.value)

        # Adjust for different scales: (a / 10^nexp_a) // (b / 10^nexp_b)
        # = (a * 10^nexp_b) // (b * 10^nexp_a)
        quotient = (a * 10 ** other.nexp) // (b * 10 ** self.nexp)

        result = PreciseNumber(sign * quotient, 0)
        result.precise = result.precise and self.precise and other.precise
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

# Constants
PreciseNumber.PI = PreciseNumber("3.14159265358979323846264338327950288419716939937510", precise=False)