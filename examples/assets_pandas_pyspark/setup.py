from setuptools import find_packages, setup

setup(
    name="assets_pandas_pyspark",
    packages=find_packages(exclude=["assets_pandas_pyspark_tests"]),
    install_requires=[
        "dagster",
        "pandas",
        "pyspark",
        # "pyarrow",
    ],
    extras_require={
        "dev": ["dagster-webserver", "pytest"],
        "test": ["pandas", "pyarrow; python_version < '3.9'", "pyspark"],
    },
)
