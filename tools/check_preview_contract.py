"""Check authored preview response fixtures against source; not a preview engine."""
import copy
import hashlib
import json
from pathlib import Path
from check_examples import tokenize

ROOT=Path(__file__).resolve().parents[1]
TOP={'spec_version','mode','status','executed','data_inspected','rules_sha256','output','plan'}
RULE={'order','name','when','message','steps'}
STEP={'order','line','operation','source','reads','writes','removes','explanation'}

def validate(plan,source):
    assert set(plan)==TOP,'Preview has unexpected or missing result properties'
    assert plan['spec_version']=='0.1-draft'
    assert plan['mode']=='preview' and plan['status']=='ready'
    assert plan['executed'] is False and plan['data_inspected'] is False and plan['output'] is None
    assert plan['rules_sha256']==hashlib.sha256(source).hexdigest()
    assert set(plan['plan'])=={'rules','warnings'}
    expected=[];current=None
    for number,line in enumerate(source.decode().splitlines(),1):
        tokens=tokenize(line)
        if not tokens:continue
        if tokens[0]=='rule':
            current={'name':json.loads(tokens[1]),'when':None,'message':None,'steps':[]};expected.append(current)
        elif tokens[0]=='when':current['when']=line.strip()[5:]
        elif tokens[0]=='message':current['message']=json.loads(tokens[1])
        else:current['steps'].append((number,tokens[0],line.strip()))
    rules=plan['plan']['rules'];assert len(rules)==len(expected)
    for index,(rule,wanted) in enumerate(zip(rules,expected),1):
        assert set(rule)==RULE and rule['order']==index
        for key in ('name','when','message'):assert rule[key]==wanted[key]
        assert len(rule['steps'])==len(wanted['steps'])
        for order,(step,(line,op,source_text)) in enumerate(zip(rule['steps'],wanted['steps']),1):
            assert set(step)==STEP and step['order']==order
            assert (step['line'],step['operation'],step['source'])==(line,op,source_text)
            assert isinstance(step['explanation'],str) and step['explanation'].strip()
            for field in ('reads','writes','removes'):
                names=step[field];assert isinstance(names,list) and all(isinstance(x,str) for x in names)
                assert names==sorted(set(names))
            if op=='check':assert not step['writes'] and not step['removes']
            if op in ('anonymize','drop'):assert step['removes'] and not step['writes']
    warnings=plan['plan']['warnings']
    assert any(w['code']=='DATA_NOT_INSPECTED' and w['rule'] is None for w in warnings)
    for warning in warnings:
        assert set(warning)=={'code','rule','message'}
        assert warning['rule'] is None or warning['rule'] in [r['name'] for r in rules]
        assert warning['code'] and warning['message']


def run():
    pairs=[('supplier-preview.json','supplier_product_feed_v1.rules'),('conditional-preview.json','conditional.rules'),('privacy-preview.json','privacy.rules')]
    fixtures=[]
    for report,source in pairs:
        plan=json.loads((ROOT/'examples'/report).read_text());raw=(ROOT/'examples'/source).read_bytes()
        validate(plan,raw);fixtures.append((plan,raw))
    catalog=json.loads((ROOT/'reference/catalog.json').read_text())
    assert catalog['preview']['response']==fixtures[0][0]
    assert catalog['preview']['cli']=='rulegenius supplier.rules --preview'
    assert catalog['preview']['api']=={'method':'POST','path':'/v1/executions','mode':'preview','parts':['rules','mode']}
    bad=[];base,source=fixtures[0]
    for key,value in [('executed',True),('data_inspected',True),('output',{'data':'not allowed'}),('mode','execute'),('status','passed'),('rules_sha256','0'*64)]:
        plan=copy.deepcopy(base);plan[key]=value;bad.append((plan,source))
    plan=copy.deepcopy(base);plan['summary']={'passed_records':2};bad.append((plan,source))
    plan=copy.deepcopy(base);plan['plan']['rules'].reverse();bad.append((plan,source))
    plan=copy.deepcopy(base);plan['plan']['rules'][0]['steps'].pop();bad.append((plan,source))
    plan=copy.deepcopy(base);plan['plan']['warnings']=[];bad.append((plan,source))
    plan=copy.deepcopy(fixtures[1][0]);plan['plan']['rules'][0]['when']=True;bad.append((plan,fixtures[1][1]))
    for plan,raw in bad:
        try:validate(plan,raw)
        except (AssertionError,KeyError,TypeError):pass
        else:raise AssertionError('Invalid preview fixture was accepted')
    print(f'PASS: {len(fixtures)} source-aligned preview fixtures and {len(bad)} rejected contract violations. No data execution performed.')

if __name__=='__main__':run()
