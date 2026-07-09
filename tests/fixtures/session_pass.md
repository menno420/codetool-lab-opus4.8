# Passing session fixture

```python {session=setup}
answer = 41
```

```python {session=setup}
answer += 1
assert answer == 42
print("shared state:", answer)
```
