# AWS Resource Explorer

A modern, user-friendly desktop application built with PySide6 that provides a visual interface for exploring AWS resources across multiple regions and profiles. The application automatically fetches AWS resources using the Resource Groups Tagging API and displays them with corresponding AWS service icons.

![AWS Resource Explorer](.media/screenshot.png)

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.0+-green.svg)
![AWS](https://img.shields.io/badge/AWS-CLI-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

- 🔐 **Multi-Profile Support**: Switch between different AWS profiles seamlessly
- 🌍 **Multi-Region Exploration**: Explore resources across all AWS regions
- 🎨 **Visual Resource Display**: View resources with official AWS service icons
- ⚡ **Asynchronous Loading**: Non-blocking UI with progress indicators
- 🔄 **Auto-Icon Management**: Automatically downloads and manages AWS icons
- 🎯 **Smart Icon Mapping**: Intelligent service-to-icon mapping with fallbacks

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** installed on your system
- **AWS CLI** configured with at least one profile
- **Git** installed and available in your PATH
- Valid AWS credentials with permissions to use Resource Groups Tagging API

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/aws-resource-explorer.git
   cd aws-resource-explorer
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify AWS configuration**:
   ```bash
   aws configure list-profiles
   aws sts get-caller-identity
   ```

### Running the Application

```bash
python window.py
```

## 📖 Usage Guide

### Basic Workflow

1. **Launch** the application
2. **Select** your AWS profile from the dropdown
3. **Choose** the target AWS region
4. **Click Load** to fetch resources
5. **Browse** through your AWS resources with visual icons

### First Run

On the first run, the application will:
- Automatically clone the AWS Icons repository
- Set up icon mapping database
- Display progress in the status bar

## 🏗️ Project Structure

```
aws-resource-explorer/
├── 📄 config.py               # AWS regions and service icon mappings
├── 🎨 form.ui                 # Qt Designer UI layout file
├── 📋 requirements.txt        # Python package dependencies
├── 🔧 ui_form.py              # Auto-generated PySide6 UI code
├── 🐍 window.py               # Main application logic and GUI
├── 📚 README.md               # Project documentation
├── 🏗️ aws-resource-explorer.pyproject  # Qt Creator project file
└── 🗂️ .qtcreator/            # Qt Creator configuration
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[AWS Icons for PlantUML](https://github.com/awslabs/aws-icons-for-plantuml)** - Official AWS icons
- **[PySide6](https://pypi.org/project/PySide6/)** - Python Qt bindings
- **[Boto3](https://boto3.amazonaws.com/)** - AWS SDK for Python
- **AWS Resource Groups Tagging API** - Resource discovery service

## 📞 Support

If you encounter any issues or have questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Search existing [Issues](https://github.com/your-username/aws-resource-explorer/issues)
3. Create a new issue with detailed information

---

**Made with ❤️ for the AWS community**