# KRA Tax Filing System

A Python-based command-line application for filing NIL tax returns with the Kenya Revenue Authority (KRA) using their official APIs.

## Features

- File NIL returns for various tax obligations (PAYE, VAT, Company Income Tax, Withholding Tax)
- Secure authentication using OAuth 2.0
- Command-line interface with rich formatting
- Automatic acknowledgment number storage
- Comprehensive error handling and validation
- Environment-based configuration

## Tax Obligations Supported

- **Income Tax - Company** (Code: 4)
- **Income Tax - Withholding** (Code: 6)
- **Income Tax - PAYE** (Code: 7)
- **Value Added Tax (VAT)** (Code: 9)

## Installation

1. Clone the repository:
```bash
cd /home/elyees/Development-env/KRA/kra-tax-filing
```

2. Install dependencies:
```bash
pip install --user requests pydantic python-dotenv click rich httpx
```

3. Configure your environment:
   - The `.env` file has been created with your credentials
   - Your KRA PIN (A017174812E) has been set as the default

## Configuration

The application uses environment variables for configuration. Your `.env` file contains:

- `KRA_CLIENT_ID`: Your KRA API consumer key
- `KRA_CLIENT_SECRET`: Your KRA API consumer secret
- `KRA_BASE_URL`: KRA API base URL (sandbox or production)
- `DEFAULT_TAXPAYER_PIN`: Your KRA PIN
- `DEFAULT_OBLIGATION_CODE`: Default tax obligation type
- `DEFAULT_MONTH`: Default month for filing
- `DEFAULT_YEAR`: Default year for filing

## Usage

### Test Connection
```bash
python main.py test-connection
```

### Check Configuration
```bash
python main.py check-config
```

### List Available Obligation Codes
```bash
python main.py list-obligations
```

### File a NIL Return

Interactive mode (will prompt for values):
```bash
python main.py file-nil
```

With command-line options:
```bash
python main.py file-nil --pin A017174812E --obligation 7 --month 11 --year 2024
```

Skip confirmation:
```bash
python main.py file-nil --pin A017174812E --obligation 7 --month 11 --year 2024 --confirm
```

## API Response Codes

### Success
- **82000**: Successfully Filed NIL Return

### Error Codes
- **82001**: XML Syntax Error
- **82002**: Data Validation Error
- **82003**: Hash Code Validation Failed
- **82004**: Invalid User ID or Password

## Acknowledgments

Successfully filed returns will generate an acknowledgment number that is:
1. Displayed in the terminal
2. Saved to the `acknowledgments/` directory with timestamp

## Project Structure

```
kra-tax-filing/
├── src/
│   ├── __init__.py
│   ├── cli.py              # Command-line interface
│   ├── kra_client.py       # KRA API client
│   ├── models.py           # Data models and validation
│   └── exceptions.py       # Custom exceptions
├── config/
│   └── settings.py         # Configuration management
├── tests/                  # Test files
├── docs/                   # Documentation
├── .env                    # Environment variables (your credentials)
├── .env.example            # Example environment file
├── main.py                 # Entry point
├── pyproject.toml          # Poetry configuration
└── README.md               # This file
```

## Security Notes

- Never commit your `.env` file to version control
- The `.env.example` file shows the required variables without sensitive data
- Your API credentials are stored locally and transmitted securely via HTTPS
- OAuth tokens are automatically refreshed when expired

## Testing in Sandbox

The application is currently configured to use the KRA sandbox environment:
- Base URL: `https://sbx.kra.go.ke`

When ready for production, update the `KRA_BASE_URL` in your `.env` file.

## Support

For issues with:
- **API Access**: Contact KRA support
- **Application Bugs**: Check the error messages and logs
- **Configuration**: Run `python main.py check-config`

## License

This project is for personal/business tax compliance purposes.