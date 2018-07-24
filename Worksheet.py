
from Parser import parse

class Sheet:
    def __init__(self):
        self.cells = {}
        self.evalchain = []

    def __repr__(self):
        return f'Sheet(Cells={len(self.cells)}, eval={len(self.evalchain)})'

    def __getattr__(self, name):
        # print(name)
        if name[0] == '_':
            return self.cells.get(name[1:])
        else:
            c = self.cells.get(name, None)
            if c is None:
                return c
            else:
                return c.value

    def add_cell(self, key, value):
        new_cell = Cell(self, key, value)
        self.cells[key] = new_cell
        return new_cell

    def cell(self, coords):
        return self.cells.get(coords, None)

    def cell_chain(self, target, include=True):
        if include:
            if target in self.evalchain:        # We are in an evaluation loop
                self.evalchain = []
                raise Exception('Evaluation Loop')
            else:
                self.evalchain.append(target)
        else:
            if target in self.evalchain:
                self.evalchain.remove(target)

    def status(self):
        print(f'Cell: {Cell.test}')
        print(self)
        for cell in self.cells.values():
            print(f' {cell}: {cell.formula} = {cell._value}')
            for ca in cell.users:
                print(f'  feeds {ca}')
            for ca in cell.sources:
                print(f'  uses  {ca}')

    def calc_formula(self, formula=None):
        s = self
        f = formula
        name_list = []
        while True:
            try:
                rv = eval(f)
                break
            except NameError as ne:
                name = ne.args[0][6:-16]  # Extract name from NameError
                if name in name_list:
                    rv = None
                    break
                if self.name_found(name):
                    f = f.replace(name, f's.{name}')
                else:
                    rv = None
                    break
        print(f'{f}={rv}')
        return rv

    def name_found(self, name):
        return name in self.cells

    def scan(self, target):
        pass


class Cell:
    test = {}

    def __init__(self, sheet, key, value):
        self.sheet = sheet
        self.key = key
        self.users = []
        self.sources = []
        self.formula = ''
        self._value = None
        self.value = value
        Cell.test[key] = self

    def __repr__(self):
        return f'Cell({self.key})'

    @property
    def value(self):
        if len(self.sheet.evalchain) > 0:          # Another cell uses us
            user_cell = self.sheet.evalchain[-1]
            if user_cell not in self.users:
                self.user(user_cell, True)
                user_cell.source(self, True)

        if self._value is None:
            return self.evaluate()
        else:
            return self._value

    @value.setter
    def value(self, value):
            self.formula = value
            if self._value is None:
                self.evaluate()
            else:
                self.evaluate(update=True)

    def source(self, source_cell, include=True):
        if include:
            if source_cell not in self.sources:
                self.sources.append(source_cell)
        else:
            if source_cell in self.sources:
                self.sources.remove(source_cell)

    def user(self, user_cell, include=True):
        if include:
            if user_cell not in self.users:
                self.users.append(user_cell)
        else:
            if user_cell in self.users:
                self.users.remove(user_cell)

    def evaluate(self, update=False):
        if update:
            self._value = None

        self.sheet.cell_chain(self, True)

        if self._value is not None:
            self.sheet.cell_chain(self, False)
            return self._value

        self._value = self.sheet.calc_formula(self.formula)

        if len(self.users) > 0:                     # Update user cells
            for user_cell in self.users:
                user_cell.evaluate(update=True)

        self.sheet.cell_chain(self, False)          # Finished evaluating this cell
        return self._value


s = Sheet()


if __name__ == "__main__":
    ca1 = s.add_cell('a1', '2 * 3')
    ca2 = s.add_cell('a2', 'a1 * 4')
    ca1.value = '3'
    s.status()
    s.calc_formula('a1 + a2 + a3')
    p = parse('a1:a2 + a3')
