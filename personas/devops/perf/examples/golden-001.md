# Perf Response
## Example Output
```
# Python — time the operation
python -m timeit -s "from module import func" "func()"

# Rust — cargo bench
cargo bench

# HTTP endpoint
hey -n 1000 -c 50 http://localhost:8000/api/endpoint
```
