import json, re, sys
from num2words import num2words

def show_lesson(lesson):
    print(lesson['title'])
    if type(lesson['content']) is str:
        print(lesson['content'])
        examples = lesson['examples']
        for example in examples:
            print(example['title'])
            print(text_transform(example_generation(example['generation'])))
            question_generation(example['generation'])
    else:
        for content in lesson['content']:
            show_lesson(content)

def create_vardict(example):
    varlist = sorted(example, key = lambda x : x['order'])
    vardict = {}
    for k in varlist:
        vardict[k['variable']] = str(eval(var_replace(k['value'], vardict)))
    return vardict

def example_generation(example):
    vardict = create_vardict(example['variables'])
    out = var_replace(example['expression'], vardict)
    match = re.search('\\$\\{([^}]+)\}', out)
    while match is not None:
        l, r = match.span()
        out = out[:l] + str(eval(out[l + 3:r - 2])) + out[r:]
        match = re.search('\\$\\{([^}]+)\}', out)
    return out

def question_generation(example):
    vardict = create_vardict(example['variables'])
    out = var_replace(example['expression'], vardict)
    match = re.search('\\$\\{([^}]+)\}', out)
    l, r = match.span()
    print(out[:l] + '?')
    while input('Answer: ') != str(eval(out[l + 3:r - 2])):
        print('Try again')
    print('Correct!')

def var_replace(s, vardict):
    inexp = s.split()
    out = []
    for i in inexp:
        if i[0] == '$' and i[1] != '{':
            out.append(vardict[i[1:]])
        else:
            out.append(i)
    return ' '.join(out)

def numerical_transform(s):
    return s

def text_transform(s):
    out = s
    match = re.search('\d+', out)
    while match is not None:
        l, r = match.span()
        out = out[:l] + 'O'*int(out[l:r]) + out[r:]
        match = re.search('\d+', out)

def picture_transform(s):
    match = re.search('\d+', s)
    out = s
    while match is not None:
        l, r = match.span()
        out = out[:l] + 'O'*int(out[l:r]) + out[r:]
    return out

with open('bedmas_lesson.json') as f:
    lesson = json.loads(f.read())
    show_lesson(lesson)
