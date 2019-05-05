import json, re, sys

def show_lesson(lesson):
    print(lesson['title'])
    if type(lesson['content']) is str:
        print(lesson['content'])
        examples = lesson['examples']
        for example in examples:
            print(example['title'])
            print(example_generation(example['generation']))
    else:
        for content in lesson['content']:
            show_lesson(content)

# s has to be a valid variable or a number
# returns value as a string
def get_value(s, variables):
    out = s[2:-1];
    m = re.fullmatch('\\w+', out)
    if m is None:
        print(m)
    else:
        out = str(variables[out])
    return out


def example_generation_old(example):
    varlist = sorted(example['variables'], key = lambda x : x['order'])
    vardict = {k['variable']: k['value'] for k in varlist}
    out = example['expression']
    match = re.search('\\$\\{([^}]+)\}', out)
    while match is not None:
        l, r = match.span()
        out = out[:l] + get_value(out[l:r], vardict) + out[r:]
        match = re.search('\\$\\{([^}]+)\}', out)
    return out

def example_generation(example):
    varlist = sorted(example['variables'], key = lambda x : x['order'])
    vardict = {}
    for k in varlist:
        vardict[k['variable']] = str(eval(var_replace(k['value'], vardict)))

    out = var_replace(example['expression'], vardict)
    match = re.search('\\$\\{([^}]+)\}', out)
    while match is not None:
        l, r = match.span()
        out = out[:l] + str(eval(out[l + 3:r - 2])) + out[r:]
        match = re.search('\\$\\{([^}]+)\}', out)
    return out

def var_replace(s, vardict):
    inexp = s.split()
    out = []
    for i in inexp:
        if i[0] == '$' and i[1] != '{':
            out.append(vardict[i[1:]])
        else:
            out.append(i)
    return ' '.join(out)

with open('bedmas_lesson.json') as f:
    lesson = json.loads(f.read())
    show_lesson(lesson)
