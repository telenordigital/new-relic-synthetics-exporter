import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="new-relic-synthetics-exporter",
    version="0.0.1",
    author="Matt Long",
    author_email="mtl@telenordigital.com",
    description="Export New Relic Synthetics results for use in Prometheus",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/telenordigital/new-relic-synthetics-exporter",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ),
)
