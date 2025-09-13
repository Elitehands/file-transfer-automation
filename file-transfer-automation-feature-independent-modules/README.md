# File Transfer Automation

Automated system for transferring batch files from a remote server to Google Drive based on Excel filter criteria.

## Features

- 🔄 Automated file transfers scheduled at 8am, 12pm, and 4pm daily
- 🔍 Smart filtering of batches based on Excel criteria
- 📂 Tracks new and updated files for incremental transfers
- 🔒 VPN connection verification and auto-reconnect
- 📝 Comprehensive logging and transaction history
- 📧 Email notifications for transfer results

## System Requirements

- Windows 10 or Windows Server 2016+
- Python 3.8 or newer (if running from source)
- Access to VPN "bbuk vpn"
- Mapped network drives:
  - Z: drive (remote server)
  - G: drive (Google Drive)

## Quick Start

### Using the Executable

1. Download the latest release
2. Extract files to desired location
3. Update configuration in `config/settings.json` if needed
4. Run `file_transfer_automation.exe`
5. Check logs in the `logs` folder

### For Developers

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create `.env` file based on `.env.example`
4. Run `python main.py`

## Configuration

The system can be configured through:
- `config/settings.json` - Main configuration file
- Environment variables (for development)

## Documentation

- [User Manual](docs/user_manual.md)
- [Troubleshooting Guide](docs/troubleshooting.md)
- [Task Scheduler Setup](docs/task_scheduler_setup.md)

## Development

- Run tests: `pytest`
- Build executable: `python build.py`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.