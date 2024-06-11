from setuptools import setup, find_packages

setup(
    name="git_commit_analyzer",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'git-commit-analyzer=git_commit_analyzer.main:main',
        ],
    },
    install_requires=[
        "pandas",
        "tabulate",
    ],
    author="Bjornar Sandvik",
    author_email="bsandvik@gmail.com",
    description="A tool to analyze git commit distribution.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/bsandvik/git_commit_analyzer",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
