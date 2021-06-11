import os

total_chars = 0
total_files = 0

for root, dirs, files in os.walk(os.path.abspath(""), topdown=False):
    for name in files:
        file_name = os.path.join(root, name)
        if not (('.git' in file_name) or ('pycache' in file_name) or ('pyc' in file_name)):
            try:
                with open(file_name, 'r') as f:
                    data = f.read()
                    total_chars += len(data)
            except:
                print(f"error : {file_name}")
            total_files += 1

print(f"Your app contain {total_chars} characters")
print(f"Your app contain {total_files} files")
