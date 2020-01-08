import sys

def ask_int(prompt, minval, maxval):
    while True:
        try:
            resp = int(input(prompt.strip() + ' '))
            if resp < minval:
                print('Value cannot be lower than %d.' % minval, file=sys.stderr)
            elif resp > maxval:
                print('Value cannot be higher than %d.' % maxval, file=sys.stderr)
            else:   # ok
                return resp
        except ValueError:
            print('Value entered is not an integer.', file=sys.stderr)

def ask_val_of_set(prompt, values_and_help):
    if len(values_and_help) == 1:
        return list(values_and_help)[0]     # return unique possible value
    values = sorted(values_and_help.keys())
    prompt = prompt.strip() + ' [' + '|'.join(values) + '|help] '
    while True:
        resp = input(prompt).strip()
        if resp in values_and_help:
            return resp
        else:
            print('Possible values are:')
            for val in sorted(values):
                print(val + ': ' + values_and_help[val])

def ask_camel_case_name(prompt, maxchars):
    while True:
        name = input(prompt.strip() + ' ').strip()
        if len(name) == 0:
            continue
        words = [ word[0].upper() + word[1:] for word in name.split() ]
        fixed_name = ''.join(words)
        if not fixed_name[0].isalpha() or not all(c.isalnum() for c in fixed_name):
            print('Name should start with a letter and contain only alphanumeric characters.', file=sys.stderr)
            continue
        if name != fixed_name:
            print('Name should be written as "CamelCase". Suggestion: "%s"' % fixed_name[:maxchars], file=sys.stderr)
            continue
        if len(name) > maxchars:
            print('Name should not be more than %d chars long.' % maxchars)
            continue
        return name

def fix_indent(num, s):
    indent = num * ' '
    lines = s.split('\n')
    return ('\n' + indent).join(lines).replace('\n' + indent + '\n', '\n\n')

def get_suffixes(num):
    if num == 1:
        return ('',)
    else:
        return tuple('_' + str(i+1) for i in range(num))

def join_blocks(blocks, sep, indent):
    code = sep.join(
        block.rstrip() for block in blocks if block != ''
    )
    if len(code) > 0 and indent > 0:
        code = fix_indent(indent, code)
    return code.rstrip()
