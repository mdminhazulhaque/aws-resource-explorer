# AWS Resource Explorer

A modern, user-friendly desktop application built with PySide6 that provides a visual interface for exploring AWS resources across multiple regions and profiles. The application automatically fetches AWS resources using the Resource Groups Tagging API and displays them with corresponding AWS service icons.

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
- 📊 **Sortable Table View**: Easy-to-navigate resource table with ARN display
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

### Supported AWS Services

The application supports all AWS services accessible through the Resource Groups Tagging API, with special icon mappings for:
- Amazon EKS (Elastic Kubernetes Service)
- Amazon EFS (Elastic File System)
- Amazon ECR (Elastic Container Registry)
- AWS IAM (Identity and Access Management)
- Amazon SES (Simple Email Service)
- Amazon EventBridge
- And many more...

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

## ⚙️ Configuration

### AWS Regions
Modify the `AWS_REGIONS` list in `config.py` to add or remove regions:

```python
AWS_REGIONS = [
    "us-east-1 (N. Virginia)",
    "us-west-2 (Oregon)",
    # Add more regions as needed
]
```

### Icon Mappings
Customize service-to-icon mappings in `config.py`:

```python
AWS_ICON_REPLACEMENTS = {
    "eks": "elastickubernetesservice",
    "iam": "iamidentitycenter",
    # Add custom mappings
}
```

## 🛠️ Development

### Setting Up Development Environment

1. **Install development dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install pytest black flake8  # Optional dev tools
   ```

2. **Modify the UI** (if needed):
   - Edit `form.ui` using Qt Designer
   - Regenerate `ui_form.py`:
     ```bash
     pyside6-uic form.ui -o ui_form.py
     ```

### Architecture

The application follows a clean architecture pattern:

- **`Window`**: Main GUI controller
- **`ResourceLoaderThread`**: Asynchronous AWS resource fetching
- **`CloneRepoThread`**: Background icon repository management
- **`config.py`**: Centralized configuration management

## 🐛 Troubleshooting

### Common Issues

**"No AWS profiles found"**
- Ensure AWS CLI is installed and configured
- Run `aws configure` to set up credentials

**"Failed to load resources"**
- Check AWS credentials and permissions
- Verify Resource Groups Tagging API access
- Ensure the selected region is accessible

**"Icons not displaying"**
- Check internet connectivity for repository cloning
- Verify Git is installed and accessible
- Check write permissions for icon cache directory

**"Application won't start"**
- Ensure Python 3.9+ is installed
- Verify all dependencies are installed
- Check for PySide6 installation issues

### Debug Mode

Run with debug output:
```bash
python -c "import sys; sys.argv.append('--debug'); exec(open('window.py').read())"
```

## 📋 Requirements

### System Requirements
- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **Python**: 3.9 or later
- **Memory**: 512MB RAM minimum
- **Storage**: 100MB free space (for icons cache)

### AWS Requirements
- Valid AWS account with configured credentials
- IAM permissions for Resource Groups Tagging API
- At least one configured AWS CLI profile

### Dependencies
See `requirements.txt` for the complete list. Key dependencies include:
- `PySide6` - GUI framework
- `boto3` - AWS SDK
- Standard library modules

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Guidelines
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

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