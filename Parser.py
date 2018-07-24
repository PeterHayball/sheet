from pyparsing import *
import Worksheet

def parse(par):

    ParserElement.enablePackrat()

    print(Worksheet.s)

    COLON, LSQ, RSQ, POS, NEG = map(Literal, ':[]+-')

    SHEET = Literal('s.')

    col_ref = Word(alphas, max=2)
    row_ref = Word(nums)
    cell_ref = Combine(Group(col_ref + row_ref))
    cell_ref.setParseAction(substCell)

    cell_ID = Combine(Group(cell_ref))('cellID')

    cell_range = Group(cell_ID('cell1') + COLON + cell_ID('cell2'))
    cell_range.setParseAction(substRange)

    expr = cell_range | cell_ID
    # expr.setParseAction(substPrint)

    par = cell_ref.transformString(par)
    par = expr.transformString(par)

    return par

def substCell(s, l, t):
    orig = t[0]
    subs = f's.{orig}'
    print(f'{orig} --> {subs}')
    return subs

def substRange(s, l, t):
    orig = t[0]
    subs = f'range({t[0][0]}, {t[0][2]})'
    print(f'{orig} --> {subs}')
    return subs

def substPrint(s, l, t):
    print(t)

