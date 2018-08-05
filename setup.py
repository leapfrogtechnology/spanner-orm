import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='spannerorm',
    version='0.1.4',
    author='Sanish Maharjan',
    author_email='sanishmaharjan@lftechnology.com',
    description='ORM for cloud spanner',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/leapfrogtechnology/spanner-orm',
    install_requires=[
        'flask',
        'google-cloud-spanner'
    ],
    packages=setuptools.find_packages(),
    classifiers=(
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ),
)
