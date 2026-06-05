#!/usr/bin/env python3
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Read the LongCoT paper
text = open('artigo/evaluations/corpus_md/2604.14140v1.txt', encoding='utf-8').read()
lines = text.split('\n')

# Print sections 2-4 (methodology)
for i, line in enumerate(lines):
    if any(line.strip().startswith(f'{n}.') for n in range(2, 7)):
        print(f'\n=== {line.strip()} ===')
        for j in range(i+1, min(i+80, len(lines))):
            l = lines[j].strip()
            if l.startswith(('2.', '3.', '4.', '5.', '6.', '7.')):
                print(f'   [...continues in section {l}]')
                break
            if l:
                print(f'   {l[:200]}')
