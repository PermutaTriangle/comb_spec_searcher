from docutils.core import publish_doctree

def is_python_block(node):
    return (node.tagname == 'literal_block'
            and 'code' in node.attributes['classes']
            and 'python' in node.attributes['classes'])

def setup_readme():
    with open('README.rst', 'r') as f:
        readme_content = f.read()
    doctree = publish_doctree(readme_content)
    code_blocks = doctree.traverse(condition=is_python_block)
    with open('test_readme.txt', 'w') as f:
        for b in code_blocks:
            f.write(b.rawsource)
            f.write('\n')

setup_readme()
