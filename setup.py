import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Function to read the list of dependencies from requirements.txt
def load_requirements(filename='requirements.txt'):
    with open(filename, 'r') as file:
        return file.read().splitlines()
    
setuptools.setup(
    name="langcache",
    version="0.0.1",
    author="Georgia Tech Database Group",
    author_email="jiashenc@gatech.edu",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jiashenC/langcache",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 1 - Planning"
    ],
    python_requires='>=3.6',
    install_requires=load_requirements(),
)
