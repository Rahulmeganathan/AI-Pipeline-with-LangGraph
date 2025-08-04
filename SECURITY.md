# Security Policy

## Supported Versions

We actively support the following versions of this project with security updates:

| Version | Supported          |
| ------- | ------------------ |
| Latest  | ✅ Yes             |
| < Latest| ❌ No              |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it by:

1. **Email**: Send details to [your-email@domain.com] with "SECURITY" in the subject line
2. **GitHub Security**: Use GitHub's private vulnerability reporting feature

### What to Include

Please include the following information in your report:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Suggested fix (if any)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Investigation**: Within 7 days
- **Fix Timeline**: Varies based on severity

## Security Best Practices

When using this application:

### API Keys and Secrets

- **Never commit** API keys to version control
- Use **environment variables** for all sensitive data
- **Rotate API keys** regularly
- Use **separate keys** for development/staging/production

### Local LLM Security

- **Monitor resource usage** when running Ollama
- **Restrict network access** to Ollama if not needed externally
- **Keep Ollama updated** to the latest version

### Vector Database Security

- Use **encrypted connections** to Qdrant Cloud
- **Limit API key permissions** to required operations only
- **Monitor access logs** regularly

### Data Privacy

- **Review documents** before uploading to ensure no sensitive data
- **Understand data flows** - some data goes to external services
- **Use local embeddings** for sensitive content

### LangSmith Security

- **Limit trace data** that includes sensitive information
- **Use appropriate project isolation** for different environments
- **Review trace data** before sharing projects

## Dependency Security

This project uses various dependencies. To maintain security:

```bash
# Check for known vulnerabilities
pip audit

# Update dependencies regularly
pip install --upgrade -r requirements.txt
```

## Infrastructure Security

### Recommended Practices

1. **Firewall Configuration**: Restrict access to only necessary ports
2. **HTTPS**: Use HTTPS for all web interfaces in production
3. **Authentication**: Implement proper authentication for production deployments
4. **Monitoring**: Set up monitoring for unusual activity
5. **Backups**: Regular backups of important data

### Environment Isolation

- Use **separate environments** for development, staging, and production
- **Different API keys** for each environment
- **Separate LangSmith projects** for each environment

## Privacy Considerations

### Data Handling

- **Document Processing**: PDFs are processed locally but metadata may be stored
- **Query Logging**: Queries may be logged in LangSmith for monitoring
- **Vector Storage**: Document embeddings are stored in Qdrant Cloud
- **Weather Data**: Weather queries are sent to OpenWeatherMap

### Compliance

- Review your **data protection requirements** (GDPR, CCPA, etc.)
- Ensure **user consent** for data processing where required
- Implement **data retention policies** as needed

## Known Security Considerations

### External Services

This application connects to:
- **LangSmith**: For tracing and monitoring
- **Qdrant Cloud**: For vector storage
- **OpenWeatherMap**: For weather data

Each service has its own privacy policy and security practices.

### Local Processing

- **Ollama**: Runs locally, data doesn't leave your machine for LLM processing
- **Local Embeddings**: Document embeddings can be generated locally

## Contact

For security-related questions or concerns:
- Create an issue with the "security" label
- Email: [your-email@domain.com]
- Use GitHub's private vulnerability reporting

---

**Note**: This is a demonstration project. For production use, conduct a thorough security review and implement appropriate security measures for your specific use case.
