import os
from tree_sitter import Language

# Direktori untuk menyimpan grammar yang di-clone
LIB_DIR = "./lib"
BUILD_PATH = "build/my-languages.so"

# Daftar grammar yang akan digunakan
LANGUAGES = {
    "go": {
        'url': "https://github.com/tree-sitter/tree-sitter-go.git",
        'path': "go"
    },
    "javascript": {
        'url': "https://github.com/tree-sitter/tree-sitter-javascript.git",
        'path': "javascript"
    },
    "php": {
        'url': "https://github.com/tree-sitter/tree-sitter-php.git",
        'path': "php/php"
    }
}

# Pastikan direktori lib/ ada
os.makedirs(LIB_DIR, exist_ok=True)

# Clone repository jika belum ada
for lang, repo in LANGUAGES.items():
    lang_dir = os.path.join(LIB_DIR, f"tree-sitter-{lang}")
    if not os.path.exists(lang_dir):
        os.system(f"git clone {repo['url']} {lang_dir}")

# Compile semua grammar ke dalam satu shared library
Language.build_library(
    BUILD_PATH,
    [os.path.join(LIB_DIR, f"tree-sitter-{lang['path']}") for lang in LANGUAGES.values()]
)

print(f"Compiled grammars: {', '.join(LANGUAGES.keys())}")
print(f"Library saved at {BUILD_PATH}")
