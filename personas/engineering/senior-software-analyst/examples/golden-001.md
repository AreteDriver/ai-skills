# Senior Software Analyst Response
## Example Output
```
# What is this project?
cat README.md | head -100
cat package.json || cat Cargo.toml || cat requirements.txt

# What's the shape?
find . -type f -name "*.rs" -o -name "*.py" -o -name "*.ts" | wc -l
find . -type d -maxdepth 2 | head -30

# Does it build?
cargo check || npm run build || python -m py_compile main.py
```
