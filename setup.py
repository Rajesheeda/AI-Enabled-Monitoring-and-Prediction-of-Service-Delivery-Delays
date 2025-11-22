"""
Setup script for GSWS SLA Monitoring System
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="gsws-sla-monitoring",
    version="1.0.0",
    author="GSWS Development Team",
    description="AI-powered system to monitor and predict service delivery delays",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/AI-Enabled-Monitoring-and-Prediction-of-Service-Delivery-Delays",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Government",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "gsws-api=run_api:main",
            "gsws-dashboard=run_dashboard:main",
            "gsws-train=app.train:main",
        ],
    },
)

