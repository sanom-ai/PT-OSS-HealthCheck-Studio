import sys
s = sys.stdin.read()
out = ''.join([l for l in s.splitlines(True) if 'Co-authored-by: Copilot' not in l])
sys.stdout.write(out)
