#!/usr/bin/env python3
"""Dependency-free draft syntax checker. Does not execute any data rules."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEYWORDS = set('rule when message check rename to split into by merge with map using convert set replace in mask anonymize drop fill reorder columns keep rows where is not required missing null a an number integer string boolean date between and or greater less than at least most true false'.split())
FUNCTIONS = {'lowercase':1,'uppercase':1,'titlecase':1,'trim':1,'round':2,'mean':1,'median':1}
TOKEN = re.compile(r'\s+|#[^\n]*|"(?:\\.|[^"\\\n])*"|`(?:``|[^`\n])+`|(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?|[A-Za-z_][A-Za-z_0-9]*|[{}\[\](),:+*/-]')

class SyntaxError(ValueError):
    pass

def tokenize(line):
    tokens=[]; position=0
    while position<len(line):
        match=TOKEN.match(line,position)
        if not match: raise SyntaxError('Unexpected character near '+repr(line[position:position+16]))
        token=match[0];position=match.end()
        if token.startswith('#'): break
        if token.isspace(): continue
        if token.startswith('"'): json.loads(token)
        tokens.append(token)
    return tokens

class Line:
    def __init__(self,tokens,aggregate=False): self.tokens=tokens;self.i=0;self.aggregate=aggregate
    def peek(self): return self.tokens[self.i] if self.i<len(self.tokens) else None
    def take(self,value=None):
        token=self.peek()
        if token is None or (value is not None and token!=value): raise SyntaxError('Expected '+repr(value)+'; got '+repr(token))
        self.i+=1;return token
    def maybe(self,value):
        if self.peek()==value:self.i+=1;return True
        return False
    def end(self):
        if self.peek() is not None: raise SyntaxError('Unexpected token '+repr(self.peek()))
    def field(self):
        token=self.take()
        if token.startswith('`'):return ('field',token[1:-1].replace('``','`'))
        if not re.fullmatch('[A-Za-z_][A-Za-z_0-9]*',token) or token in KEYWORDS:raise SyntaxError('Expected a field reference, not '+repr(token))
        return ('field',token)
    def fields(self):
        fields=[self.field()]
        while self.maybe(','):fields.append(self.field())
        if len(set(fields))!=len(fields):raise SyntaxError('Duplicate field')
    def string(self):return json.loads(self.take()) if (self.peek() or '').startswith('"') else self.expected('quoted string')
    def expected(self,what):raise SyntaxError('Expected '+what)
    def expr(self):
        node=self.term()
        while self.peek() in ('+','-'):op=self.take();node=(op,node,self.term())
        return node
    def term(self):
        node=self.unary()
        while self.peek() in ('*','/'):op=self.take();node=(op,node,self.unary())
        return node
    def unary(self):
        if self.peek() in ('+','-'):return (self.take(),self.atom())
        return self.atom()
    def atom(self):
        token=self.peek()
        if token is None:self.expected('expression')
        if self.maybe('('):node=self.expr();self.take(')');return node
        if token.startswith('"'):self.i+=1;return ('literal',json.loads(token))
        if token in ('true','false','null') or re.fullmatch(r'(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?',token):self.i+=1;return ('literal',token)
        if self.i+1<len(self.tokens) and self.tokens[self.i+1]=='(':
            name=self.take();self.take('(')
            if name not in FUNCTIONS:raise SyntaxError('Unknown function '+name)
            args=[self.expr()]
            while self.maybe(','):args.append(self.expr())
            self.take(')')
            if len(args)!=FUNCTIONS[name]:raise SyntaxError('Wrong function arity')
            if name in ('mean','median') and (not self.aggregate or args[0][0]!='field'):raise SyntaxError('Aggregates require fill and a field argument')
            return ('call',name,args)
        return self.field()
    def condition(self):
        self.conjunction()
        while self.maybe('or'):self.conjunction()
    def conjunction(self):
        self.predicate()
        while self.maybe('and'):self.predicate()
    def predicate(self):
        if self.maybe('('):self.condition();self.take(')');return
        self.field();self.take('is')
        negative=self.maybe('not')
        if self.peek() in ('missing','null'):self.take();return
        if not negative and self.maybe('required'):return
        if not negative and self.peek() in ('a','an'):
            article=self.take();kind=self.take()
            if (article,kind) not in [('a','number'),('an','integer'),('a','string'),('a','boolean'),('a','date')]:raise SyntaxError('Invalid type phrase')
            return
        if self.maybe('in'):
            self.take('[')
            if not self.maybe(']'):
                self.expr()
                while self.maybe(','):self.expr()
                self.take(']')
            return
        if not negative and self.maybe('between'):self.expr();self.take('and');self.expr();return
        if not negative and self.peek() in ('greater','less'):self.take();self.take('than');self.expr();return
        if not negative and self.maybe('at'):
            if self.take() not in ('least','most'):raise SyntaxError('Expected least or most')
            self.expr();return
        self.expr()
    def instruction(self):
        op=self.take()
        if op=='check':self.condition()
        elif op=='rename':self.field();self.take('to');self.field()
        elif op=='split':self.field();self.take('into');self.fields();self.take('by');self.string()
        elif op=='merge':self.fields();self.take('into');self.field();self.take('with');self.string()
        elif op=='map':
            self.field();self.take('using');self.take('{');keys=[]
            while True:
                keys.append(self.string());self.take(':');self.expr()
                if not self.maybe(','):break
            self.take('}')
            if len(set(keys))!=len(keys):raise SyntaxError('Duplicate map key')
        elif op=='convert':
            self.field();self.take('to')
            if self.take() not in ('number','integer','string','boolean','date'):raise SyntaxError('Invalid conversion type')
        elif op=='set':self.field();self.take('to');self.expr()
        elif op=='replace':self.expr();self.take('with');self.expr();self.take('in');self.field()
        elif op=='mask':self.field();self.take('with');self.string()
        elif op in ('anonymize','drop'):self.fields()
        elif op=='fill':self.aggregate=True;self.field();self.take('with');self.expr()
        elif op=='reorder':self.take('columns');self.fields()
        elif op=='keep':self.take('rows');self.take('where');self.condition()
        else:raise SyntaxError('Unknown instruction '+op)
        self.end();return op

def check_source(source):
    names=set();state=None
    def finish():
        if state is not None and not state['instructions']:raise SyntaxError('Rule has no instructions')
    for number,raw in enumerate(source.splitlines(),1):
        if '\t' in raw:raise SyntaxError(f'Line {number}: tabs are not allowed')
        tokens=tokenize(raw)
        if not tokens:continue
        parser=Line(tokens)
        try:
            if not raw.startswith(' '):
                finish();parser.take('rule');name=parser.string();parser.take(':');parser.end()
                if not name.strip() or name in names:raise SyntaxError('Empty or duplicate rule name')
                names.add(name);state={'instructions':0,'checks':0,'guard':False,'message':False}
            else:
                if len(raw)-len(raw.lstrip(' '))!=2 or state is None:raise SyntaxError('Expected exactly two spaces inside a rule')
                if state['message']:raise SyntaxError('Message must be last')
                if parser.maybe('when'):
                    if state['instructions'] or state['guard']:raise SyntaxError('When must be first and unique')
                    parser.condition();parser.end();state['guard']=True
                elif parser.maybe('message'):
                    if not state['checks']:raise SyntaxError('Message requires a check')
                    parser.string();parser.end();state['message']=True
                else:
                    op=parser.instruction();state['instructions']+=1;state['checks']+=op=='check'
        except (ValueError,IndexError) as error:raise SyntaxError(f'Line {number}: {error}') from error
    finish()
    if not names:raise SyntaxError('No rules')
    return len(names)

if __name__=='__main__':
    catalog=json.loads((ROOT/'reference/catalog.json').read_text())
    sources=[(x['id'],x['code']) for x in catalog['entries']]+list(catalog['examples'].items())
    sources += [(p.name,p.read_text()) for p in (ROOT/'examples').glob('*.rules')]
    for name,source in sources:
        try:check_source(source)
        except ValueError as error:raise SystemExit(f'{name}: {error}')
    invalid=json.loads((ROOT/'tests/invalid-syntax.json').read_text())
    for name,source in invalid.items():
        try:check_source(source)
        except ValueError:pass
        else:raise SystemExit('Expected rejection: '+name)
    import csv
    with (ROOT/'examples/supplier-input.csv').open() as f:assert len(list(csv.DictReader(f)))==2
    with (ROOT/'examples/supplier-output.csv').open() as f:assert len(list(csv.DictReader(f)))==2
    print(f'PASS: {len(sources)} source examples accepted; {len(invalid)} invalid syntax cases rejected; CSV fixtures readable. No runtime execution performed.')
