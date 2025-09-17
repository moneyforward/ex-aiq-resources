#!/usr/bin/env python3
import argparse
import json
import sys
from jsonschema import Draft7Validator

def main():
    ap = argparse.ArgumentParser(description='Validate expense_rulebook.json against schema')
    ap.add_argument('--schema', default='expense_rulebook.schema.json')
    ap.add_argument('--rulebook', default='expense_rulebook.json')
    args = ap.parse_args()

    try:
        with open(args.schema, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        with open(args.rulebook, 'r', encoding='utf-8') as f:
            rb = json.load(f)
    except Exception as e:
        print(f'ERROR: failed to read files: {e}', file=sys.stderr)
        return 2

    errors = sorted(Draft7Validator(schema).iter_errors(rb), key=lambda e: e.path)
    if errors:
        print(f'Validation failed: {len(errors)} error(s)')
        for e in errors:
            path = '/'.join(str(p) for p in e.path)
            print(f'- {path}: {e.message}')
        return 1
    print('Validation passed')
    return 0

if __name__ == '__main__':
    sys.exit(main())
